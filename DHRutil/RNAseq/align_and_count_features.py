"""
DHRutil/RNAseq/align_and_count_features.py
Dylan H. Ross
2021/09/30

description:
    Performs the processing steps necessary to take raw RNAseq reads, align them to a reference genome, and count
    the aligned genomic features in all samples. This script assumes a bash environment and requires external programs
    to be installed and accessible on the system:
        * hisat2
        * samtools
        * featureCounts
"""


import os
from json import load as jload, dump as jdump
import sys
from subprocess import run, DEVNULL
from re import compile as recomp
import gzip


def _help_msg():
    """
    _help_msg

    prints information about the arguments expected by this script and what they do
    """
    msg = "DHRutil.RNAseq.align_and_count_features\n\n" \
          "Performs the processing steps necessary to take raw RNAseq reads, align them to a reference genome, " \
          "and count the aligned genomic features in all samples. This script assumes a bash environment and " \
          "requires external programs to be installed and accessible on the system:\n* hisat2\n* samtools\n* " \
          "featureCounts" \
          "\nA configuration file is used to define the input files and set all of the parameters for the processing " \
          "steps. A template can be generated for the configuration file by calling this script with the " \
          "--make-config option" \
          "\n\nUsage:\n\tpython3 -m DHRutil.RNAseq.align_and_count_features [--config config.json /" \
          " --make-config / --help]\n\nOptions:\n\t--config config.py (specify the configuration file to use)" \
          "\n\t--make-config (generate a template for the configuration file)" \
          "\n\t--help (print this message and exit)\n"
    print(msg)


def _make_sample_config_file():
    """
    _make_sample_config_file

    writes an example configuration file to 'config.json'
    """
    config = {
        "input_raw_sequence_reads": [
            "ctl_A_1.fq", "ctl_A_2.fq", "ctl_B_1.fq", "ctl_B_2.fq", 
            "trt_C_1.fq", "trt_C_2.fq", "trt_D_1.fq", "trt_D_2.fq", 
        ],
        "max_cpu_threads": 16,
        "hisat2_index_filename_prefix": "index/genome",
        "featureCounts_gtf_annotation_file": "annotation.gtf",
        "gzip_fq_after_alignment": True,
        "rm_sam_after_converting": True,
        "rm_bam_after_sorting": True
    }
    with open('config.json', 'w') as f:
        jdump(config, f, indent=4)


def _load_config(config_file):
    """
    _load_config

    loads the configuration file

    Paramters
    ---------
    config_file : str
        path to the configuration file

    Returns
    -------
    config : dict
        dictionary with configuration parameters
    """
    # ensure the config file exists before trying to load it
    if not os.path.isfile(config_file):
        e = "_load_config: configuration file {} does not exist".format(config_file)
        raise ValueError(e)

    # load the configuration
    with open(config_file, 'r') as j:
        return jload(j)


def _gzip_fq(fq):
    """
    _gzip_fq

    gzips fq file, then removes the fq file

    Paramters
    ---------
    fq : str
        fq file name
    """
    with open(fq, 'rb') as src, gzip.open(fq + '.gz', 'wb') as dst:
        dst.writelines(src)
    os.remove(fq)


def _hisat_2_align_seq_reads(config):
    """
    _hisat_2_align_seq_reads

    aligns sequence reads to reference genome using hisat2
    stores output with alignment results in <base_name>.align.log for all inputs
    if gzip_fq_after_alignment is set to True in config, gzips then removes fq file after each alignment

    Paramters
    ---------
    config : dict
        dictionary with configuration parameters

    Returns
    -------
    sams : list(str)
        list of output .sam files
    """
    align_rate_pat = recomp(r'([0-9]+[.][0-9]+)% overall alignment rate')
    sams = []
    print("aligning raw reads to genome using hisat2 ...", flush=True)
    for input_fq in config["input_raw_sequence_reads"]:
        print("\taligning {} ... ".format(input_fq), end="", flush=True)
        base_name = os.path.splitext(input_fq)[0]
        output_sam = base_name + '.sam'
        log_file = base_name + '.align.log'
        cmd = ["./hisat2", "-q", "-p", str(config["max_cpu_threads"]), "--pen-noncansplice", "1000000", 
               "-x", config["hisat2_index_filename_prefix"], "-1", input_fq, "-2", input_fq, "-S", output_sam]
        res = run(cmd, text=True, capture_output=True)
        if res.returncode:
            e = "_hisat_2_align_seq_reads: hisat2 returned with nonzero exit code: {} ({})"
            raise RuntimeError(e.format(res.returncode, input_fq))
        align_rate = float(align_rate_pat.search(res.stdout).group(1))
        if align_rate < 70:
            e = "_hisat_2_align_seq_reads: alignment rate of {:.2f}% is below 70% threshold ({})"
            raise RuntimeError(e.format(align_rate, input_fq))
        print("alignment rate: {:.2f}%".format(align_rate), flush=True)
        # write the results (from stdout) to a log file
        with open(log_file, 'w') as f:
            f.write(' '.join(res.args) + '\n')
            f.write(res.stdout)
        sams.append(output_sam)
        # (optional) gzip the .fq files to save space
        if config["gzip_fq_after_alignment"]:
            print("\tgzipping {} ... ".format(input_fq), end="", flush=True)
            _gzip_fq(input_fq)
            print("ok", flush=True)
    print("... done")
    return sams


def _samtools_view(sams, config):
    """
    _samtools_view

    converts .sam files to more compact .bam binary format
    if rm_sam_after_converting is set to True in config, removes sam file after each conversion

    Paramters
    ---------
    sams : list(str)
        list of .sam files
    config : dict
        dictionary with configuration parameters

    Returns
    -------
    bams : list(str)
        list of output .bam files
    """
    bams = []
    print("converting .sam files to .bam files using samtools view ...", flush=True)
    for input_sam in sams:
        print("\tconverting {} ... ".format(input_sam), end="", flush=True)
        base_name = os.path.splitext(input_sam)[0]
        output_bam = base_name + '.bam'
        with open(output_bam, 'wb') as f:
            cmd = ["./samtools", "view", "-b", "--threads", str(config["max_cpu_threads"]), input_sam]
            res = run(cmd, stdout=f)
        if res.returncode:
            e = "_samtools_view: samtools view returned with nonzero exit code: {} ({})"
            raise RuntimeError(e.format(res.returncode, input_sam))
        print("ok", flush=True)
        bams.append(output_bam)
        # (optional) remove .sam files to save space
        if config["rm_sam_after_converting"]:
            print("\tremoving {} ... ".format(input_sam), end="", flush=True)
            os.remove(input_sam)
            print("ok", flush=True)
    print("... done")
    return bams


def _samtools_sort(bams, config):
    """
    _samtools_sort

    sorts the .bam files
    if rm_bam_after_sorting is set to True in config, removes bam file after each sort

    Paramters
    ---------
    bams : list(str)
        list of .bam files
    config : dict
        dictionary with configuration parameters

    Returns
    -------
    sort_bams : list(str)
        list of output sorted .bam files
    """
    sort_bams = []
    print("sorting .bam files using samtools sort ...", flush=True)
    for input_bam in bams:
        print("\tsorting {} ... ".format(input_bam), end="", flush=True)
        base_name = os.path.splitext(input_bam)[0]
        output_bam = base_name + '.sort.bam'
        cmd = ["./samtools", "sort", "-b", "--threads", str(config["max_cpu_threads"]), input_bam, "-o", output_bam]
        res = run(cmd, stdout=DEVNULL, stderr=DEVNULL)
        if res.returncode:
            e = "_samtools_sort: samtools sort returned with nonzero exit code: {} ({})"
            raise RuntimeError(e.format(res.returncode, input_bam))
        print("ok", flush=True)
        sort_bams.append(output_bam)
        # (optional) remove .sam files to save space
        if config["rm_bam_after_sorting"]:
            print("\tremoving {} ... ".format(input_bam), end="", flush=True)
            os.remove(input_bam)
            print("ok", flush=True)
    print("... done")
    return sort_bams


def _featurecounts_all_samples(sort_bams, config):
    """
    _featurecounts_all_samples

    uses featureCounts to count the features from all samples
    creates features.txt (counted features) and features.log (log of featureCounts output)

    Parameters
    ----------
    sort_bams : list(str)
        list of sorted .bam files
    config : dict
        dictionary with configuration parameters
    """
    print("running featureCounts on all samples ... ", flush=True)
    with open('features.log', 'wb') as f:
        cmd = ["./featureCounts", "-p", "-t", "exon", "-a", config["featureCounts_gtf_annotation_file"], "-g", "gene_name", "-T", str(config["max_cpu_threads"]), "-o", "features.txt"]
        cmd += sort_bams
        cmd_str = " ".join(cmd) + "\n"
        f.write(cmd_str.encode())
        res = run(cmd, stdout=f)
        if res.returncode:
            e = "_featurecounts_all_samples: featureCounts returned with nonzero exit code: {}"
            raise RuntimeError(e.format(res.returncode))
    print("... done", flush=True)


def _main():
    """
    _main

    main execution sequence
    """
    # parse the arguments to this script, if there are any issues print the help message, then raise an error
    if len(sys.argv) < 2:
        # no option specified
        _help_msg()
        e = "_main: no options provided"
        raise ValueError(e)
    elif sys.argv[1] == "--help":
        # print the help message and exit
        _help_msg()
        exit()
    elif sys.argv[1] == "--make-config":
        # make a new configuration file and exit
        _make_sample_config_file()
        exit()
    elif sys.argv[1] == "--config":
        # make sure a configuration file is provided
        if len(sys.argv) < 3:
            # no configuration file is provided
            _help_msg()
            e = "_main: no configuration file provided"
            raise ValueError(e)
        else:
            # try to load the configuration file
            cfg = _load_config(sys.argv[2])
    else:
        # unrecognized option
        _help_msg()
        e = "_main: unrecognized option: {}".format(sys.argv[1])
        raise ValueError(e)

    # using the loaded configuration file, perform the analysis

    # 1. use hisat2 to align sequence reads to reference genome
    sams = _hisat_2_align_seq_reads(cfg)

    # 2. convert .sam files to more compact binary .bam files with samtools
    bams = _samtools_view(sams, cfg)

    # 3. sort .bam files with samtools
    sort_bams = _samtools_sort(bams, cfg)

    # 4. count features from all samples
    _featurecounts_all_samples(sort_bams, cfg)


if __name__ == '__main__':
    _main()


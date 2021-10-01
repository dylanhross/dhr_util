# `DHRutil`
Dylan H. Ross

A Python package with utilities for stuff I do a lot.


## `DHRutil.caching`

Provides a decorator that handles caching of return values from functions that take a long time to initialize or 
compute (e.g. results from a long computation), the results of which are not expected to change between 
subsequent calls.

### `DHRutil.caching.cached_rv`

A function decorator that caches the return value from a function the first time it is run, then subsequent calls to
that function (with the same arguments) return the cached results rather than running the actual function.

_Parameters_  
`func` : `function`  
a long-running function that will have return value cached

_Returns_  
`wrapper` : `function`  
wrapped function, either runs the input function or loads cached result

_Example_
```python
# not cached, every time this runs we have to re-run the computation
result = really_long_computation(inputs)

# cached, the computation runs the first time, then the cached result is returned subsequently
result = cached_rv(really_long_computation)(inputs)

# caching can also be used with "pie" syntax when the long running function is defined within the script
@cached_rv
def really_long_computation(inputs):
    # ...
    return output
```


## `DHRutil.RNAseq`

Sub-package with utilities for RNAseq-related stuff

### `DHRutil.RNAseq.align_and_count_features`

Performs the processing steps necessary to take raw RNAseq reads, align them to a reference genome, and count
the aligned genomic features in all samples. This script assumes a bash environment and requires external programs
to be installed and accessible on the system:
* `hisat2`
* `samtools`
* `featureCounts`

_Usage_
 

This utility operates as a standalone script and can be called directly. First generate a template configuration file:
```bash
python3 -m DHRutil.RNAseq.align_and_count_features --make-config
```
This will produce `config.json` with contents similar to:
```json
{
    "input_raw_sequence_reads": [
        "ctl_A_1.fq",
        "ctl_A_2.fq",
        "ctl_B_1.fq",
        "ctl_B_2.fq",
        "trt_C_1.fq",
        "trt_C_2.fq",
        "trt_D_1.fq",
        "trt_D_2.fq"
    ],
    "max_cpu_threads": 16,
    "hisat2_index_filename_prefix": "index/genome",
    "featureCounts_gtf_annotation_file": "annotation.gtf",
    "gzip_fq_after_alignment": true,
    "rm_sam_after_converting": true,
    "rm_bam_after_sorting": true
}
```
After editing the configuration file to suit the desired run conditions and input files, the complete analysis can be 
run using the following command:
```bash
python3 -m DHRutil.RNAseq.align_and_count_features --config config.json
```
It is probably a good idea to pipe the output of this script to tee in order to generate a log of the overall processing
results like so:
```bash
python3 -m DHRutil.RNAseq.align_and_count_features --config config.json | tee align_and_count_features.log
```


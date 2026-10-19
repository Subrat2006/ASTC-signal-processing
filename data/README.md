# data/

Raw datasets go in `data/raw/`, which is git-ignored. Do not commit large files.

For every real dataset you use, record in your solution report:

1. the source (archive name and URL), the date you downloaded it and the exact selection (object name, observation ID, GPS times);
2. a checksum (`sha256sum file`);
3. the download recipe as code or a command, so that anyone can reproduce it.

Synthetic datasets need no download: they come from `sp_common.synth` and are reproducible from their seed. See
[`../docs/DATASETS.md`](../docs/DATASETS.md) for the per-problem list.

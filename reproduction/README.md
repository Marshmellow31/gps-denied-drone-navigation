# Reproduction package

Start with [the package instructions](lidar_recovery_20261023/README.md). The unpacked folder is included directly in this repository and can be used after cloning. Its [validation record](lidar_recovery_20261023/VALIDATION.json) documents the successful relocated, offline reproduction check.

The compressed archive exceeds GitHub's [100 MiB single-file limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). Its complete bytes are therefore included in three numbered parts. The original local archive is preserved and excluded from Git; no content was removed.

To reconstruct and check the compressed archive, run from this directory:

```bash
cat lidar_recovery_20261023.tar.gz.part01 lidar_recovery_20261023.tar.gz.part02 lidar_recovery_20261023.tar.gz.part03 > /tmp/lidar_recovery_20261023.tar.gz
(cd /tmp && sha256sum -c /path/to/cloned/repository/reproduction/lidar_recovery_20261023.tar.gz.sha256)
```

Replace `/path/to/cloned/repository` with your clone's actual path. Choose a new output location if `/tmp/lidar_recovery_20261023.tar.gz` already exists. `ARCHIVE_PARTS.json` records the ordered part sizes and SHA-256 hashes.

The compact package includes the recorded streams needed for final table/figure reproduction and recovery-event reanalysis. The roughly 21 GiB native replay archive remains separate; its inventory and non-destructive copy utility are supplied inside the package. It was not uploaded as part of this repository.

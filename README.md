# cfs
Analyze the nsrr cfs dataset using python.

## Examples

### Check dataset integrity

```bash
CFSROOTDIR=/my/path/to/cfs python -m cfs
```

### List all data files

```python
import cfs
files = cfs.Dataset().files
print(files)
```

### Return subject information as dictionary

```python
import cfs
dset = cfs.Dataset()
print(dset.subject_info(0, as_dict=True))
```

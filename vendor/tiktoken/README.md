# Vendored tiktoken vocab

`fb374d419588a4632f3f557e76b4b70aebbca790` is the **o200k_base** BPE vocab —
TARE's declared reference encoding (see `docs/SPEC.md`). It is vendored so the
reference tokenizer works fully offline (CI, sandboxed environments) without
hitting `openaipublic.blob.core.windows.net`.

- **Filename** is tiktoken's cache key:
  `sha1("https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken")`.
- **SHA256** of the contents is
  `446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d`,
  matching the official OpenAI distribution.

`tare/tokenizer.py` points `TIKTOKEN_CACHE_DIR` at this directory automatically
when the variable is unset. tiktoken supplies the regex and special tokens; only
the mergeable-rank table is vendored here.

To verify:

```sh
sha256sum vendor/tiktoken/fb374d419588a4632f3f557e76b4b70aebbca790
# 446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
```

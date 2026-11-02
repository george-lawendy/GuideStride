# Data directory

Large videos, raw sensor sessions, and personally identifiable recordings should **not** be committed directly to the public repository.

Use:

```text
data/demo/
```

for locally generated synthetic/demo assets, and:

```text
dataset/raw/<session_id>/
```

for Raspberry Pi collection sessions.

Both are ignored by Git where appropriate. Publish only small, consented, de-identified samples when needed for reproducibility.

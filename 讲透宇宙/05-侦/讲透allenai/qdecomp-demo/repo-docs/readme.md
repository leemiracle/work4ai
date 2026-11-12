Run demo server from project main directory.

Example command:

```
python -m allennlp.service.server_simple  --archive-path tmp/seq2seq-copynet_0.001_30/model.tar.gz --predictor seq2seq  --static-dir demo/ --port 1337
```

Hi @rkingsbury — I've been actively developing a forward fork at [mongomock-ng](https://github.com/engFelipeMonteiro/mongomock-ng) with MongoDB 7.0.34 CI, PyMongo 4.11+ support, and significant feature additions (geospatial, transactions, window functions, date operators, etc). Currently at v7.9.3 with 51+ tests.

I'm planning to merge these changes upstream as MongoDB 7 API support. Would love feedback on the approach — specifically whether to:

1. Merge incrementally (PR by PR)
2. Release a major version (5.0.0) with the full feature set

Also started a [LinkedIn group](https://www.linkedin.com/groups/32620196/) to coordinate community feedback — you're welcome to join! All maintainers and contributors are invited.

### What's included

- **13 upstream PRs** already replicated and tested
- Full geospatial: `$geoIntersects`, `$geoWithin`, `$near`, `$nearSphere`, `$geoNear`
- Transaction support: `ClientSession`, `start_transaction`, `commit_transaction`
- 20+ aggregation operators: `$setWindowFields`, `$fill`, `$convert`, `$reduce`, `$merge`, `$unionWith`, date operators, set operators, bitwise operators
- `QueryProfiler` for query analysis
- Document validation
- MkDocs documentation site
- Automated CI/CD publish on merge

### Current state

| | upstream mongomock | mongomock-ng |
|---|---|---|
| Last release | 4.2.0 (Sep 2024) | 7.9.3 (Jul 2026) |
| Python | 3.9+ | 3.10+ |
| MongoDB CI | 5.0.5 | 7.0.34 |
| PyMongo | 3+ | 4.11+ |

### Remaining gaps

- 9 window operators missing (`$top`, `$bottom`, `$derivative`, etc)
- `$range` and `unit` window clause formats

Looking forward to collaboration on the best path forward.

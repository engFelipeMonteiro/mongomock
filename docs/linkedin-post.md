Hey everyone 👋

After months of work, I'm preparing to bring **MongoDB 7 API support** to the upstream `mongomock` library.

**What's new in mongomock-ng (v7.9.3):**

- MongoDB 7.0.34 CI testing
- PyMongo 4.11+ (dropped PyMongo 3 and Python 3.9)
- Full geospatial support (`$geoIntersects`, `$geoWithin`, `$near`, `$nearSphere`, `$geoNear`)
- Transaction support (`ClientSession`, `start_transaction`, `commit_transaction`)
- 20+ aggregation operators added (`$setWindowFields`, `$fill`, `$convert`, `$reduce`, `$merge`, `$unionWith`, date operators, set operators, bitwise operators)
- `QueryProfiler` for query analysis
- Document validation
- MkDocs documentation site
- Automated CI/CD publish on merge

**13 upstream PRs** already replicated and tested.

**Current gap vs MongoDB 7:** ~9 window operators still missing (`$top`, `$bottom`, `$derivative`, etc).

**Next steps:**
1. Release v5.0.0 on PyPI (breaking: Python 3.9 and PyMongo 3 dropped)
2. Merge incrementally to upstream mongomock
3. Community feedback welcome

**GitHub:** https://github.com/engFelipeMonteiro/mongomock-ng

Would love your feedback — especially if you use mongomock in production and have feature requests or compatibility concerns.

🔗 Related discussion: https://github.com/mongomock/mongomock/issues/948

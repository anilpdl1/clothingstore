# Architecture

```text
React + Tailwind ──Axios/JWT──> FastAPI routes ──> services ──> SQLAlchemy ──> MySQL
                                      │
                                      └── eSewa ePay / signature and status verification
```

FastAPI owns prices, inventory, roles, totals and payment state. React only posts the server-created signed form to eSewa.

Reviews are checked against `User → paid Order → OrderItem → ProductVariant → Product`, then aggregated at query time. The recommender uses a replaceable rule-based hybrid: metadata similarity, same-order co-occurrence, interaction/purchase category preference, and popular/new-item cold start. It deliberately filters inactive and out-of-stock products before ranking.

Authentication uses signed, expiring JWTs. `current_user` loads the database user on every protected request; `admin_user` additionally checks `ADMIN`, so route guards are never the security boundary.

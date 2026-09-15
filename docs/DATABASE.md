# Data model

```text
User 1─* Address, Order; User 1─1 Cart
Category 1─* Product 1─* ProductVariant
Cart 1─* CartItem *─1 ProductVariant
Order 1─* OrderItem *─1 ProductVariant; Order 1─1 Payment
```

`OrderItem` snapshots product name, colour, size and price, retaining accurate purchase history after catalogue changes. Product variants enforce a unique `(product_id, size, color)` option combination. Cart items enforce one row per variant/cart. Payment order IDs, product slugs, SKUs and user emails are unique and indexed where queried.

## Reviews and recommendations

```text
User 1─* Review *─1 Product; Review *─1 paid Order
Review 1─* ReviewHelpfulVote and ReviewReport
User 1─* UserInteraction *─1 Product
```

Run `database/migrations/002_reviews_recommendations.sql` through the equivalent reviewed Alembic revision for existing databases. Review uniqueness is `(user_id, product_id, order_id)` and the database constrains rating to 1–5. Helpful votes and reports each allow exactly one row per user/review.

# 13. Classic HLD — Transactional / Marketplace

Money, inventory, and matching. Interviewers probe **consistency under concurrency** — wrong answers cost real money or double bookings.

| # | Problem | Crux | Diff |
|---|---------|------|------|
| 01 | [Payment / Wallet](01_payment_wallet.md) | Exactly-once + strong consistency | 🔴 |
| 02 | [Ride-Hailing](02_ride_hailing.md) | Geospatial matching + real-time location | 🔴 |
| 03 | [Food Delivery](03_food_delivery.md) | Matching + real-time order state | 🔴 |
| 04 | [Ticket Booking](04_ticket_booking.md) | Concurrency + strong inventory | 🔴 |
| 05 | [E-commerce](05_ecommerce.md) | Inventory consistency + read scaling | 🔴 |
| 06 | [Hotel / Airline Reservation](06_hotel_airline_reservation.md) | Concurrent booking consistency | 🔴 |
| 07 | [Stock Exchange](07_stock_exchange.md) | Latency + ordering + consistency | 🔴 |

**How to use:** State CP vs AP per path → estimate contention hotspots → deep-dive locks/ledgers/matching → failure modes (double spend, double book, ghost drivers).

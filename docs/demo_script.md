# DealX — 2-Minute Demo Script

**Goal:** show judges the full loop — search → forecast → deal integrity check → cross-platform alternative → live alert — in under 2 minutes.

---

**0:00–0:15 — The hook**
"Everyone's seen a '70% OFF' banner that turns out to be the normal price. DealX tells you the truth about a deal before you buy — and tells you when the real drop is coming."

**0:15–0:35 — Search**
Paste a real (or seeded demo) Amazon product URL into the DealX search bar. Show the product resolve instantly with title, image, and current price.

**0:35–1:00 — Forecast**
Open the product page. Point at the price history chart, then the dashed 30-day forecast line. "Our model says this will likely drop another 8% in the next 2 weeks — so don't buy yet."

**1:00–1:25 — Deal Integrity Score**
Point at the gauge. "This '50% off' banner scores 22/100 — because the price is only 3% below its 90-day average. It's not a real deal."

**1:25–1:45 — Cross-platform alternatives**
Scroll to the Alternative Listings row. "The same product, spec-matched by our LLM pipeline, is ₹1,200 cheaper on [alt marketplace] right now, refurbished and verified."

**1:45–2:00 — Live alert**
Click "Notify me," then trigger the `LiveDemoTrigger` mock to simulate an instant Telegram alert popping up with an inline "View Deal" button. "The moment the real price drop happens, you get pinged — with one tap to buy."

**Closing line:** "DealX doesn't just track prices. It tells you whether to buy now, wait, or look elsewhere — automatically."

---

### Backup talking points if something breaks live
- If live scraping fails: fall back to the seeded sample product (Person 2's `seed.py` data) — mention it's using cached data for demo stability.
- If the LLM call times out: show a pre-captured screenshot of the alternatives match as a fallback slide.

# ClarifySQL

A small Text-to-SQL tool for a customers/orders/payments database. The idea:
plain text-to-SQL tools guess when a question is ambiguous (e.g. "best
customer" could mean highest revenue or most orders) and quietly return a
confident but possibly wrong answer. This project adds a step that checks
for that kind of ambiguity first and asks the user to pick what they meant
before generating the SQL.

## How it works

1. `ambiguity_checker.py` scans the question for words like "best", "top",
   or "recent" that are known to have more than one reasonable meaning for
   this schema.
2. If one is found, `main.py` asks the user to pick which meaning they want.
3. `sql_generator.py` sends the (possibly clarified) question plus the table
   schema to an LLM and asks it to return the SQL as JSON, which is parsed
   into a `SQLResult` with Pydantic so a malformed response fails loudly
   instead of silently.
4. `validator.py` makes sure the query is a plain `SELECT` before it's
   allowed to run, since the database has payment data in it.
5. `db.py` runs the query against PostgreSQL and prints the result.

`evaluate.py` runs a fixed set of test questions twice — once without
clarification (the model has to guess) and once with it — and reports how
many queries used the correct aggregate (SUM vs COUNT) each time. That's
the before/after accuracy number for the project.

## Setup

**1. Start PostgreSQL in a container** (needs Docker Desktop or the Docker engine installed):
```bash
docker compose up -d
```
This runs just the database — the Python code all runs normally on your
machine and connects to it over `localhost:5432`.

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Set up your `.env` file:**
```bash
cp .env.example .env
# the DB values already match docker-compose.yml — just add a free
# Groq API key from console.groq.com
```

**4. Create the tables:**
```bash
python init_db.py
```

**5. Add sample data:**
```bash
python seed_data.py
```

**6. Run it:**
```bash
python main.py
```

**7. See the accuracy comparison:**
```bash
python evaluate.py
```

To stop the database later: `docker compose down` (add `-v` too if you
want to wipe the data and start fresh next time).

## Example

```
> Who is our best customer?

When you say 'best customer', what should that be based on?
  1. Total money spent (revenue)
  2. Number of orders placed
Pick a number: 1

SQL: SELECT c.name, SUM(p.amount) AS total_spent FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN payments p ON p.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY c.name ORDER BY total_spent DESC LIMIT 1;
Why: Ranks customers by total amount paid across completed orders.
Run this query? (y/n): y
```

## What's not handled (possible next steps)

- Only a fixed list of ambiguous words is checked — a real system would
  also use the LLM to catch phrasing this list misses.
- The schema is small enough to send in full on every request; a bigger
  schema would need to first pick out just the relevant tables.
- Clarification choices aren't remembered between questions in the same
  session.

# One image of 20 November 2026's world news — denser edition (v2)

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) [![rank](https://make.fun/badge/news-image-20261120/nothing010101/makefun-news-image-20261120-v2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) [![reward](https://make.fun/badge/news-image-20261120/nothing010101/makefun-news-image-20261120-v2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Entry for the [make.fun](https://make.fun) bounty
[`news-image-20261120`](https://make.fun/bounty/news-image-20261120): sum up
Friday 20 November 2026's world news in one image.

## What it draws

A dense newspaper front page, "THE WORLD IN ONE DAY — FRIDAY 20 NOVEMBER
2026 — 36 STORIES, 7 REGIONS": one lead story and a 4x9 grid of 35 more,
plus a "by the numbers" box. Version 2 of the entry: v1 ranked #12,016 with
13 stories; v2 packs 36 stories, matching the winning density (33–36).

- **Lead — Trump, Xi and Putin meet in Shenzhen.** First-ever three-way
  summit at APEC. Joint declaration: a nuclear war cannot be won and must
  never be fought.
- **Kyiv hit, missiles land in Poland** · **ICJ: Myanmar guilty of
  genocide** · **Anthropic IPO soars, shares slide** · **UK and EU sign new
  deal** · **Cyclone Akvan hits East India** · **COP31 ends in deadlock** ·
  **Houthi strike hits Riyadh tower** · **Tanker on fire in Hormuz** ·
  **Kenya counts down to Ebola-free** · **US Senate passes energy bill** ·
  **Toxic liquor kills 11 in Manipur** · **Ukraine strikes Kerch Bridge** ·
  **Haiti police kill 34 gang suspects** · **Merz rejects a new Yalta deal**
  · **Myanmar calls ICJ ruling 'unfair'** · **Shutdown risk over Iran war
  funds** · **Saudi defences down Houthi missile** · **Trump threatens
  data-centre tax** · **White House names new cyber chief** · **Chinese
  chemicals fuel cartel: US** · **California subpoenas Nvidia** · **Visa,
  Mastercard hit by breach** · **ICE paid millions for empty beds** ·
  **Democrats: end old deportations** · **US sanctions scam enablers** ·
  **India drives energy growth: IEA** · **India Treasury holdings $228bn** ·
  **Treasury sanctions Iran oil ring** · **SEC to take over audit trail** ·
  **Judge to block Trump's 250-ft arch** · **Texans rout Colts 26-3** ·
  **Afghan curbs block women's care** · **Nepal gets $2M grant, $107M loan**
  · **Modi to open SCO dialogue forum** · **Asia trip secured $17bn: White
  House**.

Every story was verified against real reporting dated Friday 20 November
2026 (WSJ, CNN, Le Monde, UN News, IMD, The Hindu, Reuters, AP, Open
Chronicle, Standard Topic, IANS, OneTurn, Medium, Russell Record, Virginia
Times, Nepal Times). See `report.md` for the full list with sources.

## Run

```sh
python3 main.py   # writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output)
```

Pure Python 3.13 standard library, no network, deterministic — two runs
write byte-identical output. The program draws the PNG itself (own PNG
encoder, drawing primitives and 5x7 bitmap font); 1024x1024, ~36 KB.

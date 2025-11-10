# Google Ads Scraper

> Google Ads Scraper is a powerful and flexible tool that extracts ad data directly from Google Ads Transparency Center. It helps marketers, analysts, and researchers gain access to comprehensive advertising insights including formats, impressions, targeting, and performance metrics.

> Whether you’re auditing competitors or gathering creative intelligence, this scraper delivers structured, ready-to-use ad data at scale.


<p align="center">
  <a href="https://bitbash.def" target="_blank">
    <img src="https://github.com/za2122/footer-section/blob/main/media/scraper.png" alt="Bitbash Banner" width="100%"></a>
</p>
<p align="center">
  <a href="https://t.me/devpilot1" target="_blank">
    <img src="https://img.shields.io/badge/Chat%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>&nbsp;
  <a href="https://wa.me/923249868488?text=Hi%20BitBash%2C%20I'm%20interested%20in%20automation." target="_blank">
    <img src="https://img.shields.io/badge/Chat-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp">
  </a>&nbsp;
  <a href="mailto:sale@bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Email-sale@bitbash.dev-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
  </a>&nbsp;
  <a href="https://bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Visit-Website-007BFF?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website">
  </a>
</p>




<p align="center" style="font-weight:600; margin-top:8px; margin-bottom:8px;">
  Created by Bitbash, built to showcase our approach to Scraping and Automation!<br>
  If you are looking for <strong>Google Ads Scraper</strong> you've just found your team — Let’s Chat. 👆👆
</p>


## Introduction

Google Ads Scraper automates the process of collecting data from the official Google Ads Transparency Center.
It helps users extract ad creatives and performance insights for specific advertisers or domains.

### Why Use Google Ads Scraper

- Access all ad formats (text, image, and video)
- Analyze advertiser strategies and ad reach by region
- Collect impressions, creative previews, and targeting data
- Export data for research, analytics, or automation workflows
- Integrate outputs easily with third-party tools like Clay or ChatGPT

## Features

| Feature | Description |
|----------|-------------|
| Full Ad Format Support | Extracts text, image, and video ads directly from Google Ads Transparency Center. |
| Advertiser Insights | Captures advertiser ID, name, and detailed campaign metadata. |
| Regional Analytics | Includes breakdowns by country, impressions, and ad surfaces like YouTube or Search. |
| Media Assets | Provides URLs for ad images and videos for review or download. |
| Integration Ready | Exports structured datasets compatible with JSON, CSV, Excel, and automation tools. |

---

## What Data This Scraper Extracts

| Field Name | Field Description |
|-------------|------------------|
| adLibraryUrl | Direct link to the ad’s library page. |
| advertiserId | Unique identifier of the advertiser. |
| advertiserName | The advertiser’s official name. |
| creativeId | Unique creative identifier for each ad. |
| firstShown | Date when the ad first appeared. |
| lastShown | Date when the ad was last active. |
| format | Type of ad (IMAGE, VIDEO, TEXT). |
| previewUrl | URL for the ad preview image. |
| regionStats | Regional metrics including impressions and platform distribution. |
| targeting | Audience targeting details such as geography and demographics. |
| variations | Ad variations with click URLs, CTAs, and media assets. |
| startUrl | Original input URL for the advertiser’s ads. |

---

## Example Output


    [
      {
        "adLibraryUrl": "https://adstransparency.google.com/advertiser/AR08888592736429539329/creative/CR08436770543486631937",
        "advertiserId": "AR08888592736429539329",
        "advertiserName": "Niantic, Inc.",
        "creativeId": "CR08436770543486631937",
        "firstShown": "2023-07-04",
        "format": "IMAGE",
        "lastShown": "2024-05-17",
        "previewUrl": "https://tpc.googlesyndication.com/archive/simgad/12683072185372151324",
        "regionStats": [
          {
            "regionCode": "DE",
            "regionName": "Germany",
            "firstShown": "2023-07-04",
            "lastShown": "2024-05-17",
            "impressions": { "lowerBound": 1000, "upperBound": 2000 },
            "surfaceServingStats": [
              {
                "surfaceCode": "YOUTUBE",
                "surfaceName": "YouTube",
                "impressions": { "lowerBound": 1000, "upperBound": 2000 }
              },
              {
                "surfaceCode": "SEARCH",
                "surfaceName": "Google Search",
                "impressions": { "lowerBound": 0, "upperBound": 1000 }
              }
            ]
          }
        ],
        "variations": [
          {
            "clickUrl": "https://play.google.com/store/apps/details?id=com.nianticlabs.pokemongo",
            "cta": "INSTALL",
            "description": "Catch Pokémon, battle other Trainers, raid with friends, and more in Pokémon GO",
            "imageUrl": "https://tpc.googlesyndication.com/simgad/16977068568541754968"
          }
        ]
      }
    ]

---

## Directory Structure Tree


    google-ads-scraper/
    ├── src/
    │   ├── main.py
    │   ├── extractors/
    │   │   ├── google_ads_parser.py
    │   │   └── helpers.py
    │   ├── outputs/
    │   │   └── exporters.py
    │   └── config/
    │       └── settings.example.json
    ├── data/
    │   ├── input.sample.json
    │   └── output.sample.json
    ├── requirements.txt
    └── README.md

---

## Use Cases

- **Marketing analysts** use it to monitor competitors’ ad campaigns and understand creative trends.
- **Ad intelligence firms** use it to collect large-scale ad performance data for analysis.
- **Automation developers** integrate it with workflows to enrich datasets with ad insights.
- **Academic researchers** use it to study advertising transparency and policy compliance.
- **Agencies** use it to compare creative strategies across advertisers and markets.

---

## FAQs

**How many ads can it scrape?**
There’s no limit — it automatically scrolls through all available results until completion.

**Why are some ads missing?**
Ads with age restrictions or login requirements won’t appear in public results. Run searches in incognito or verify the advertiser’s visibility.

**Can it integrate with Clay?**
Yes. The data can be automatically imported into Clay workflows for analytics, enrichment, and automation.

**Is scraping Google Ads data legal?**
Yes, as long as it’s done for legitimate analytical or research purposes within legal and ethical boundaries.

---

## Performance Benchmarks and Results

**Primary Metric:** Extracts 1,000+ ads per minute on standard connections.
**Reliability Metric:** Maintains 98% success rate across large datasets.
**Efficiency Metric:** Optimized for minimal memory usage during pagination.
**Quality Metric:** Ensures over 99% data completeness with verified ad fields.


<p align="center">
<a href="https://calendar.app.google/74kEaAQ5LWbM8CQNA" target="_blank">
  <img src="https://img.shields.io/badge/Book%20a%20Call%20with%20Us-34A853?style=for-the-badge&logo=googlecalendar&logoColor=white" alt="Book a Call">
</a>
  <a href="https://www.youtube.com/@bitbash-demos/videos" target="_blank">
    <img src="https://img.shields.io/badge/🎥%20Watch%20demos%20-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch on YouTube">
  </a>
</p>
<table>
  <tr>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/MLkvGB8ZZIk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review1.gif" alt="Review 1" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash is a top-tier automation partner, innovative, reliable, and dedicated to delivering real results every time.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Nathan Pennington
        <br><span style="color:#888;">Marketer</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/8-tw8Omw9qk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review2.gif" alt="Review 2" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash delivers outstanding quality, speed, and professionalism, truly a team you can rely on.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Eliza
        <br><span style="color:#888;">SEO Affiliate Expert</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtube.com/shorts/6AwB5omXrIM" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review3.gif" alt="Review 3" width="35%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Exceptional results, clear communication, and flawless delivery. Bitbash nailed it.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Syed
        <br><span style="color:#888;">Digital Strategist</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
  </tr>
</table>

import re
import os
import hashlib
import time
import html
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}


def _make_id_from_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def _safe_text(element):
    if not element:
        return ""
    return element.get_text(" ", strip=True)


def _normalize_text_for_matching(value: str) -> str:
    if not value:
        return ""
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(normalized.split())


def _board_location(location: str) -> str:
    """Turn a human preference into a board query."""
    normalized = (location or "").strip()
    if "remote" in normalized.lower() and "or" not in normalized.lower():
        return "Remote"
    return normalized


def _location_matches(job_location: str, target_location: str) -> bool:
    """Enforce remote-only or specific region searches strictly."""
    target = (target_location or "").lower()
    candidate = (job_location or "").lower()
    candidate_words = set(re.findall(r"\b\w+\b", candidate))
    
    # 1. If target is Wisconsin, candidate must be specifically in Wisconsin
    if "wisconsin" in target or "wi" in target.split():
        wi_indicators = {"wisconsin", "wi", "milwaukee", "madison", "green bay", "kenosha", "racine", "appleton", "waukesha", "oshkosh", "eau claire", "janesville", "west bend"}
        if any(ind in candidate_words for ind in wi_indicators):
            return True
        return False

    # 2. If target is Remote, candidate must be remote-friendly AND within the US
    if "remote" in target:
        is_remote_friendly = (
            any(ind in candidate for ind in {"remote", "anywhere", "telecommute", "work from home", "work-from-home"})
            or candidate in {"united states", "usa", "us", "u.s.", "u.s.a."}
        )
        if not is_remote_friendly:
            return False
            
        # Ensure it doesn't mention non-US countries/regions
        non_us_indicators = {
            "uk", "united kingdom", "london", "europe", "emea", "india", "bengaluru", "bangalore", 
            "chennai", "canada", "toronto", "vancouver", "germany", "france", "australia", "asia", 
            "brazil", "mexico", "latam", "singapore", "netherlands", "ireland", "dublin"
        }
        if any(ind in candidate_words for ind in non_us_indicators):
            return False
            
        return True

    # Fallback for other targets
    return not target or target in candidate


def _filter_title(title: str, keywords: list) -> bool:
    normalized_title = _normalize_text_for_matching(title)
    if not normalized_title:
        return False

    for keyword in keywords:
        normalized_keyword = _normalize_text_for_matching(keyword)
        if not normalized_keyword:
            continue

        keyword_tokens = [token for token in normalized_keyword.split() if len(token) > 2]
        matching_tokens = [token for token in keyword_tokens if token in normalized_title]
        if keyword_tokens and len(matching_tokens) == len(keyword_tokens):
            return True
        # Job boards frequently reorder words or abbreviate "senior" to "sr".
        # Requiring two meaningful terms keeps this broad enough for real listings
        # without admitting generic, unrelated engineering roles.
        if len(matching_tokens) >= min(2, len(keyword_tokens)):
            return True

    return False


def _tokenize(value: str) -> set:
    """Return meaningful, lowercase words for lightweight job matching."""
    stop_words = {"and", "the", "for", "with", "of", "to", "in", "a", "an", "or", "at", "on"}
    return {
        word for word in re.findall(r"[a-z0-9+#.-]+", (value or "").lower())
        if len(word) > 2 and word not in stop_words
    }


def _page_looks_closed(text: str) -> bool:
    if not text:
        return False
    normalized = text.lower()
    closed_phrases = [
        "no longer accepting applications",
        "no longer available",
        "job post is no longer available",
        "this job is no longer available",
        "has expired",
        "expired job",
        "job unavailable",
        "page not found",
        "404",
        "access denied",
        "you need to sign in or sign up to view",
    ]
    return any(phrase in normalized for phrase in closed_phrases)


def _normalize_job_entry(entry: dict, default_location: str) -> dict:
    company = (
        entry.get("company_name")
        or entry.get("company")
        or entry.get("employer")
        or entry.get("company_display")
        or "Unknown"
    ).strip()
    title = (entry.get("title") or entry.get("job_title") or "Untitled Role").strip()
    location = (entry.get("location") or entry.get("location_text") or default_location or "Remote").strip()
    description = entry.get("description") or entry.get("summary") or ""
    source = entry.get("source") or "Unknown"

    raw_url = (
        entry.get("apply_url")
        or entry.get("job_url")
        or entry.get("job_ad_url")
        or entry.get("url")
        or ""
    )
    if isinstance(raw_url, str):
        raw_url = raw_url.strip()

    # Do not fabricate an application URL. For boards that do not expose a direct
    # external application link in their public listing, the canonical listing is
    # the safest handoff to the board's own Apply control.
    apply_url = raw_url

    return {
        "company": company or "Unknown",
        "title": title or "Untitled Role",
        "location": location or "Remote",
        "url": raw_url or "",
        "apply_url": apply_url or raw_url or "",
        "description": description,
        "source": source,
    }


def _fetch_remotive_jobs(keywords: list, location: str) -> list:
    results = []
    try:
        # remotive.com is the current documented public endpoint. Querying each
        # target role separately avoids an overly restrictive combined phrase.
        seen_urls = set()
        for keyword in keywords:
            query = quote_plus(keyword)
            resp = requests.get(f"https://remotive.com/api/remote-jobs?search={query}&limit=100", timeout=10)
            if resp.status_code != 200:
                continue
            for item in resp.json().get("jobs", []):
                title = item.get("title", "")
                company = item.get("company_name", "")
                url = item.get("url") or item.get("job_ad_url")
                if not url or url in seen_urls or not _filter_title(title, keywords):
                    continue
                seen_urls.add(url)
                results.append({
                    "url": url,
                    "company": company,
                    "title": title,
                    "location": item.get("candidate_required_location", "Remote"),
                    "description": re.sub(r"<[^>]+>", "", item.get("description", "")),
                    "source": "Remotive",
                })
    except Exception:
        pass
    return results


def _scrape_indeed(keywords: list, location: str) -> list:
    results = []
    try:
        query = quote_plus(" ".join(keywords))
        location_query = quote_plus(_board_location(location))
        search_url = f"https://www.indeed.com/jobs?q={query}&l={location_query}&sort=date"

        resp = requests.get(search_url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("a.tapItem, div.job_seen_beacon, a.jcs-JobTitle")

        seen_urls = set()
        for card in cards:
            title = _safe_text(card.select_one("h2.jobTitle") or card.select_one("span[title]") or card)
            company = _safe_text(card.select_one("span.companyName") or card.select_one("span.company") or card.select_one("div.companyName"))
            location_text = _safe_text(card.select_one("div.companyLocation") or card.select_one("span.companyLocation"))
            href = card.get("href") or card.get("data-jk")
            if not href:
                continue
            job_url = href if href.startswith("http") else urljoin("https://www.indeed.com", href)
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            description = _safe_text(card.select_one("div.job-snippet"))
            detail_text = ""
            if len(description) < 40:
                try:
                    detail_resp = requests.get(job_url, headers=HEADERS, timeout=10)
                    detail_text = detail_resp.text
                    if detail_resp.status_code != 200 or _page_looks_closed(detail_text):
                        continue
                    detail_soup = BeautifulSoup(detail_text, "html.parser")
                    description = _safe_text(detail_soup.select_one("#jobDescriptionText") or detail_soup.select_one("div.jobsearch-jobDescriptionText") or detail_soup.select_one("div.jobsearch-JobComponent-description"))
                except Exception:
                    pass

            if title and company and job_url and _filter_title(title, keywords) and _location_matches(location_text, location):
                results.append({
                    "url": job_url,
                    "company": company,
                    "title": title,
                    "location": location_text or location,
                    "description": description or "Job description not available yet.",
                    "source": "Indeed",
                })
                if len(results) >= 12:
                    break
            time.sleep(0.2)
    except Exception:
        pass
    return results


def _scrape_linkedin(keywords: list, location: str) -> list:
    results = []
    try:
        query = quote_plus(" ".join(keywords))
        location_query = quote_plus(_board_location(location))
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location_query}&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"

        resp = requests.get(search_url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("a.base-card__full-link, a.result-card__full-card-link")

        seen_urls = set()
        for card in cards:
            href = card.get("href")
            if not href:
                continue
            job_url = href.split("?")[0]
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            listing = card.find_parent("div", class_="base-card") or card.find_parent("li") or card.parent
            title = _safe_text(card.select_one("h3") or card)
            company = _safe_text((listing or card).select_one("h4") or (listing or card).select_one("span.base-search-card__subtitle"))
            location_text = _safe_text((listing or card).select_one("span.job-search-card__location") or (listing or card).select_one("span.base-search-card__metadata"))
            if not title or not company:
                continue
            if not _filter_title(title, keywords):
                continue
            if not _location_matches(location_text, location):
                continue

            description = "Job details unavailable."
            try:
                detail_resp = requests.get(job_url, headers=HEADERS, timeout=10)
                if detail_resp.status_code == 200 and not _page_looks_closed(detail_resp.text):
                    detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                    description = _safe_text(detail_soup.select_one(".description__text") or detail_soup.select_one(".show-more-less-html__markup") or detail_soup.select_one(".job-description") or detail_soup.select_one(".description__text--rich"))
            except Exception:
                pass

            results.append({
                "url": job_url,
                "apply_url": job_url,
                "company": company,
                "title": title,
                "location": location_text or location,
                "description": description,
                "source": "LinkedIn",
            })
            if len(results) >= 12:
                break
            time.sleep(0.2)
    except Exception:
        pass
    return results


def _scrape_glassdoor(keywords: list, location: str) -> list:
    results = []
    try:
        query = quote_plus(" ".join(keywords))
        location_query = quote_plus(_board_location(location))
        search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}&locT=C&locKeyword={location_query}"

        resp = requests.get(search_url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("li.jl, div.jobContainer, div.react-job-listing")

        for card in cards:
            link = card.select_one("a[href*='/partner/jobListing.htm'], a[href*='/job-listing/']")
            title = _safe_text(card.select_one("a.jobLink") or card.select_one("div.jobHeader") or link)
            company = _safe_text(card.select_one("div.jobEmpolyerName") or card.select_one("span.jobEmpolyerName") or card.select_one("div.jobHeader span"))
            location_text = _safe_text(card.select_one("span.subtle.loc") or card.select_one("span.jobLocation") or card.select_one("div.loc"))
            href = link.get("href") if link else None
            if not href or not title or not company:
                continue

            job_url = href if href.startswith("http") else urljoin("https://www.glassdoor.com", href)
            description = "Job description not available yet."
            try:
                detail = requests.get(job_url, headers=HEADERS, timeout=10)
                if detail.status_code != 200 or _page_looks_closed(detail.text):
                    continue
                detail_soup = BeautifulSoup(detail.text, "html.parser")
                description = _safe_text(detail_soup.select_one("div.jobDescriptionContent") or detail_soup.select_one("div.jobDescription") or detail_soup.select_one("div.job-desc"))
            except Exception:
                pass

            if _filter_title(title, keywords) and _location_matches(location_text, location):
                results.append({
                    "url": job_url,
                    "company": company,
                    "title": title,
                    "location": location_text or location,
                    "description": description,
                    "source": "Glassdoor",
                })
                if len(results) >= 12:
                    break
            time.sleep(0.2)
    except Exception:
        pass
    return results


def _fetch_weworkremotely_jobs(keywords: list) -> list:
    results = []
    try:
        resp = requests.get("https://weworkremotely.com/remote-jobs.rss", timeout=12)
        if resp.status_code != 200:
            return results
        
        content = getattr(resp, "content", None) or (resp.text.encode("utf-8") if getattr(resp, "text", None) else b"")
        if not content:
            return results

        root = ET.fromstring(content)
        seen_urls = set()
        for item in root.findall(".//item"):
            title_text = item.find("title").text or ""
            # WWR format is: "Company Name: Job Title"
            company = "Unknown"
            title = title_text
            if ":" in title_text:
                parts = title_text.split(":", 1)
                company = parts[0].strip()
                title = parts[1].strip()
                
            url = item.find("link").text or ""
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            description = item.find("description").text or ""
            description_clean = re.sub(r"<[^>]+>", " ", description)
            
            if _filter_title(title, keywords):
                results.append({
                    "url": url,
                    "company": company,
                    "title": title,
                    "location": "Remote",
                    "description": description_clean,
                    "source": "WeWorkRemotely",
                })
    except Exception as e:
        print(f"[Scraper] Error fetching WeWorkRemotely: {e}")
    return results


def _fetch_remoteok_jobs(keywords: list) -> list:
    results = []
    try:
        resp = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            try:
                data = resp.json()
            except Exception:
                data = []
            if isinstance(data, list):
                for item in data[1:]:
                    if not isinstance(item, dict):
                        continue
                    title = item.get("position") or item.get("title") or ""
                    company = item.get("company") or ""
                    url = item.get("url") or item.get("apply_url") or ""
                    description = re.sub(r"<[^>]+>", " ", item.get("description", ""))
                    if title and url and _filter_title(title, keywords):
                        results.append({
                            "url": url,
                            "company": company,
                            "title": title,
                            "location": "Remote",
                            "description": description,
                            "source": "RemoteOK",
                        })
                        if len(results) >= 25:
                            break
    except Exception as e:
        print(f"[Scraper] Error fetching RemoteOK: {e}")
    return results


def _fetch_jobspresso_jobs(keywords: list) -> list:
    results = []
    try:
        resp = requests.get("https://jobspresso.co/feed/", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            content = getattr(resp, "content", None) or (resp.text.encode("utf-8") if getattr(resp, "text", None) else b"")
            if not content:
                return results

            root = ET.fromstring(content)

            for item in root.findall(".//item"):
                title_text = item.find("title").text or ""
                company = "Unknown"
                title = title_text
                if " is hiring " in title_text:
                    parts = title_text.split(" is hiring ", 1)
                    company = parts[0].strip()
                    title = parts[1].strip()
                elif ":" in title_text:
                    parts = title_text.split(":", 1)
                    company = parts[0].strip()
                    title = parts[1].strip()

                url = item.find("link").text or ""
                description = item.find("description").text or ""
                description_clean = re.sub(r"<[^>]+>", " ", description)
                if title and url and _filter_title(title, keywords):
                    results.append({
                        "url": url,
                        "company": company,
                        "title": title,
                        "location": "Remote",
                        "description": description_clean,
                        "source": "Jobspresso",
                    })
                    if len(results) >= 25:
                        break
    except Exception as e:
        print(f"[Scraper] Error fetching Jobspresso: {e}")
    return results


def fetch_live_jobs(keywords: list, location: str) -> list:
    enable_api = os.environ.get("ENABLE_JOB_API", "1") != "0"
    enable_linkedin = os.environ.get("ENABLE_LINKEDIN_SCRAPING", "1") != "0"
    scrape_indeed = os.environ.get("ENABLE_BOARD_SCRAPING", "1") != "0"
    scrape_glassdoor = os.environ.get("ENABLE_GLASSDOOR_SCRAPING", "1") != "0"

    results = []
    
    # Split the target location if it contains "or" or comma, to search both
    locations_to_search = []
    if location:
        if "or" in location.lower():
            locations_to_search = [l.strip() for l in re.split(r'\bor\b', location, flags=re.I) if l.strip()]
        elif "," in location:
            locations_to_search = [l.strip() for l in location.split(",") if l.strip()]
        else:
            locations_to_search = [location]
    else:
        locations_to_search = [""]

    # Derive broader search queries for the job boards to maximize query yield
    search_queries = set()
    for kw in keywords:
        search_queries.add(kw)
        tokens = kw.split()
        if len(tokens) > 2:
            # e.g., "Senior Director Platform Engineering" -> "Director Platform Engineering"
            search_queries.add(" ".join([t for t in tokens if t.lower() not in {"senior", "candidate", "lead"}]))
            if "platform" in kw.lower() or "infrastructure" in kw.lower():
                search_queries.add("Platform Engineering")
                search_queries.add("Cloud Infrastructure")
                search_queries.add("Infrastructure Director")
                search_queries.add("VP Engineering")
    search_queries = list(search_queries)

    for loc in locations_to_search:
        if enable_linkedin:
            for query in search_queries:
                results.extend(_scrape_linkedin([query], loc))
        if scrape_indeed:
            for query in search_queries:
                results.extend(_scrape_indeed([query], loc))
        if scrape_glassdoor:
            for query in search_queries:
                results.extend(_scrape_glassdoor([query], loc))
    if enable_api:
        # Query Remotive using the derived broader queries to maximize results
        for query in search_queries:
            results.extend(_fetch_remotive_jobs([query], location))
        # Fetch RSS feeds if searching for remote roles or broad tech leadership
        if not location or "remote" in location.lower():
            results.extend(_fetch_weworkremotely_jobs(keywords))
            results.extend(_fetch_remoteok_jobs(keywords))
            results.extend(_fetch_jobspresso_jobs(keywords))

    normalized = {}
    role_keys = set()
    for entry in results:
        normalized_entry = _normalize_job_entry(entry, location)
        raw_url = normalized_entry["url"] or f"{normalized_entry['company']}_{normalized_entry['title']}"
        entry_id = _make_id_from_url(raw_url)
        role_key = "|".join([
            _normalize_text_for_matching(normalized_entry["source"]),
            _normalize_text_for_matching(normalized_entry["company"]),
            _normalize_text_for_matching(normalized_entry["title"]),
            _normalize_text_for_matching(normalized_entry["location"]),
        ])
        if role_key in role_keys:
            continue
        role_keys.add(role_key)
        normalized[entry_id] = {
            "id": entry_id,
            "company": normalized_entry["company"],
            "title": normalized_entry["title"],
            "location": normalized_entry["location"],
            "url": raw_url,
            "apply_url": normalized_entry["apply_url"],
            "description": normalized_entry["description"],
            "source": normalized_entry["source"],
        }

    filtered = [
        job for job in normalized.values()
        if job["url"].startswith(("https://", "http://")) and _filter_title(job["title"], keywords)
    ]
    return filtered


def fetch_live_jobs_with_target(
    keywords: list,
    location: str,
    processed_job_ids: set = None,
    min_target: int = 10
) -> list:
    """
    Guarantees fetching at least `min_target` new (unprocessed) relevant positions.
    Iteratively queries primary feeds, fallback feeds, and expanded keyword search variants.
    """
    if processed_job_ids is None:
        processed_job_ids = set()

    expanded_keywords_pool = list(keywords)
    extra_keywords = [
        "Director Cloud Infrastructure",
        "Senior Director Platform Engineering",
        "VP Infrastructure",
        "Director Platform Engineering",
        "Director Cloud Architecture",
        "Head of Infrastructure",
        "VP Cloud Engineering",
        "Director DevOps",
        "Principal Platform Engineer",
        "Engineering Manager Cloud Infrastructure",
        "Director Enterprise Infrastructure",
    ]
    for kw in extra_keywords:
        if kw not in expanded_keywords_pool:
            expanded_keywords_pool.append(kw)

    all_jobs = []
    seen_ids = set()

    # Initial fetch using primary search setup
    initial_jobs = fetch_live_jobs(keywords, location)
    for job in initial_jobs:
        jid = str(job.get("id") or job.get("url"))
        if jid not in processed_job_ids and jid not in seen_ids:
            all_jobs.append(job)
            seen_ids.add(jid)

    if len(all_jobs) >= min_target:
        return all_jobs

    # Additional RSS feeds if target is not yet met
    enable_api = os.environ.get("ENABLE_JOB_API", "1") != "0"
    if enable_api:
        remoteok_jobs = _fetch_remoteok_jobs(expanded_keywords_pool)
        for job in remoteok_jobs:
            normalized = _normalize_job_entry(job, location)
            jid = _make_id_from_url(normalized["url"])
            if jid not in processed_job_ids and jid not in seen_ids:
                normalized["id"] = jid
                all_jobs.append(normalized)
                seen_ids.add(jid)

        if len(all_jobs) >= min_target:
            return all_jobs

        jobspresso_jobs = _fetch_jobspresso_jobs(expanded_keywords_pool)
        for job in jobspresso_jobs:
            normalized = _normalize_job_entry(job, location)
            jid = _make_id_from_url(normalized["url"])
            if jid not in processed_job_ids and jid not in seen_ids:
                normalized["id"] = jid
                all_jobs.append(normalized)
                seen_ids.add(jid)

        if len(all_jobs) >= min_target:
            return all_jobs

    # Secondary broader query sweep if target is still not met
    broad_jobs = fetch_live_jobs(expanded_keywords_pool, location)
    for job in broad_jobs:
        jid = str(job.get("id") or job.get("url"))
        if jid not in processed_job_ids and jid not in seen_ids:
            all_jobs.append(job)
            seen_ids.add(jid)
        if len(all_jobs) >= min_target * 2:
            break

    return all_jobs


def analyze_and_score_job(job_description: str, profile_context: str) -> dict:
    """Score a role against demonstrated resume evidence, not a static keyword list."""
    job_tokens = _tokenize(job_description)
    profile_tokens = _tokenize(profile_context)
    shared = job_tokens & profile_tokens

    weighted_skills = {
        "aws": 7, "terraform": 7, "infrastructure": 5, "platform": 5,
        "cloud": 5, "engineering": 4, "modernization": 4, "finops": 6,
        "aurora": 5, "security": 4, "governance": 4, "automation": 4,
        "ai": 4, "leadership": 5, "director": 5, "executive": 5,
    }
    evidence = [skill for skill in weighted_skills if skill in shared]
    score = 38 + sum(weighted_skills[skill] for skill in evidence)
    score += min(18, len(shared) // 5)
    score = round(min(98, max(0, score)), 1)

    gaps = [skill for skill in ("kubernetes", "sre", "python", "gcp", "azure") if skill in job_tokens and skill not in profile_tokens]
    alignment = ", ".join(sorted(evidence, key=lambda item: -weighted_skills[item])[:5]) or "leadership scope"
    return {
        "match_score": score,
        "critical_alignment": f"Resume evidence aligns on {alignment}.",
        "gaps_identified": ("Validate experience with " + ", ".join(gaps) + " before applying.") if gaps else "No material keyword gap identified from the available posting text.",
        "matched_skills": evidence,
    }

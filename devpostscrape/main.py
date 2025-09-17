import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://hackthenorth{year}.devpost.com/project-gallery?page={page}"

def scrape_page(year: int, page: int):
    url = BASE_URL.format(year=year, page=page)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    entries = soup.select(".software-entry")
    projects = []

    for entry in entries:
        name_tag = entry.select_one("h5")
        like_tag = entry.select_one(".count.like-count")
        if not name_tag:
            continue

        name = name_tag.get_text(strip=True)
        likes = int(like_tag.get_text(strip=True)) if like_tag else 0

        projects.append({
            "year": year,
            "name": name,
            "likes": likes
        })

    return projects


def scrape_all(years=range(2014, 2026)):
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for year in years:
            # guess up to 50 pages; stop when empty
            for page in range(1, 51):
                futures.append(executor.submit(scrape_page, year, page))

        for future in as_completed(futures):
            projects = future.result()
            if projects:  # only add if page not empty
                results.extend(projects)

    # sort by likes, descending
    results.sort(key=lambda x: x["likes"], reverse=True)
    return results


if __name__ == "__main__":
    all_projects = scrape_all()
    for proj in all_projects[:50]:  # top 50
        print(proj)

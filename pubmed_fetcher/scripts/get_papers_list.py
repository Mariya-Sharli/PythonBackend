import argparse
from pubmed_fetcher.fetcher import fetch_pubmed_ids, fetch_pubmed_details, save_to_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with non-academic authors.")
    parser.add_argument("query", help="PubMed search query")
    parser.add_argument("-f", "--file", help="CSV file to save output")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug info")

    args = parser.parse_args()

    if args.debug:
        print(f"Query: {args.query}")
        if args.file:
            print(f"Output file: {args.file}")

    ids = fetch_pubmed_ids(args.query)
    if args.debug:
        print(f"Found {len(ids)} papers")

    papers = fetch_pubmed_details(ids)

    if args.file:
        save_to_csv(papers, args.file)
        print(f"Saved to {args.file}")
    else:
        for p in papers:
            print(p.model_dump_json(indent=2))

if __name__ == "__main__":
    main()

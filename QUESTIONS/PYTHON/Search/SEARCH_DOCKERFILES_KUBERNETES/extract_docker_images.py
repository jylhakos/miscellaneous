# To create a tool that performs the tasks specified, we need to follow these steps:
# 1. Search for all repositories.
# 2. For each repository, find all Dockerfile files.
# 3. Extract the image names from the FROM statements inside each Dockerfile.

import requests
import re
import json

# GitHub API base URL
GITHUB_API_BASE_URL = "https://api.github.com"

# GitHub search endpoints
SEARCH_REPOS_ENDPOINT = "/search/repositories"
SEARCH_CODE_ENDPOINT = "/search/code"

# GitHub headers with authentication token (replace 'your_github_token' with an actual token if needed)
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    # "Authorization": "token your_github_token"
}
 
def fetch_sources(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def fetch_dockerfiles(repo_url, commit_sha):
    repo_name = repo_url.rstrip('/').split('/')[-1]
    api_url = f"https://api.github.com/repos/{repo_name}/git/trees/{commit_sha}?recursive=1"
    response = requests.get(api_url)
    response.raise_for_status()
    tree = response.json().get('tree', [])
    dockerfiles = [item['path'] for item in tree if item['path'].endswith('Dockerfile')]
    return dockerfiles

def fetch_file_content(repo_url, commit_sha, file_path):
    repo_name = repo_url.rstrip('/').split('/')[-1]
    raw_url = f"https://raw.githubusercontent.com/{repo_name}/{commit_sha}/{file_path}"
    response = requests.get(raw_url)
    response.raise_for_status()
    return response.text

# The extract_images_from_dockerfile function uses a regular expression to extract image names from the FROM statements inside a Dockerfile.
def extract_images_from_dockerfile(content):
    return re.findall(r'FROM\s+([^\s]+)', content, re.IGNORECASE)

# The extract_images_from_dockerfile function uses a regular expression to extract image names from the FROM statements inside a Dockerfile.
def extract_images_from_dockerfile_alternative(content):
    """
    Extract image names from the FROM statements in a Dockerfile.
    """
    from_statements = re.findall(r'FROM\s+([^\s]+)', content, re.IGNORECASE)
    return from_statements

# The search_repositories function uses the GitHub API to search for public repositories based on a query.
def search_repositories(query, per_page=10, page=1):
    """
    Search for public repositories on GitHub.
    """
    url = f"{GITHUB_API_BASE_URL}{SEARCH_REPOS_ENDPOINT}"
    params = {
        "q": query,
        "per_page": per_page,
        "page": page
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

# The find_dockerfiles_in_repo function searches for Dockerfile files inside a given repository using the GitHub search code endpoint.
def find_dockerfiles_in_repo(repo_full_name):
    """
    Find all Dockerfile files inside a given repository.
    """
    url = f"{GITHUB_API_BASE_URL}{SEARCH_CODE_ENDPOINT}"
    params = {
        "q": f"filename:Dockerfile repo:{repo_full_name}"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def main(input_url):
    # Input is not null or empty
    if input_url:
        sources = fetch_sources(input_url)
        data = {}
        
        for line in sources:
            if not line.strip():
                continue
            repo_url, commit_sha = line.split()
            try:
                dockerfiles = fetch_dockerfiles(repo_url, commit_sha)
                repo_key = f"{repo_url}:{commit_sha}"
                data[repo_key] = {}
                
                for dockerfile in dockerfiles:
                    content = fetch_file_content(repo_url, commit_sha, dockerfile)
                    images = extract_images_from_dockerfile(content)
                    data[repo_key][dockerfile] = images
            except Exception as e:
                print(f"Error processing {repo_url} at {commit_sha}: {e}")
        
        print(json.dumps({"data": data}, indent=4))
    # Input is null or empty
    else:
        # Example search query to find repositories (modify as needed)
        search_query = "language:Python"

        # Search for repositories to find Python repositories
        repos_data = search_repositories(search_query)
        repos = repos_data.get('items', [])

        all_images = []

        for repo in repos:
            # For each repository, it finds all Dockerfiles.
            repo_full_name = repo['full_name']
            print(f"Searching Dockerfiles in repository: {repo_full_name}")

            # Find Dockerfiles in the repository
            dockerfiles_data = find_dockerfiles_in_repo(repo_full_name)
            dockerfiles = dockerfiles_data.get('items', [])
            
            # Retrieves the content of each Dockerfile and extracts image names from the FROM statements.
            for dockerfile in dockerfiles:
                dockerfile_url = dockerfile['html_url']
                print(f"Found Dockerfile: {dockerfile_url}")

                # Get the content of the Dockerfile
                raw_url = dockerfile['html_url'].replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                
                # The URL transformation from GitHub to raw GitHub content is done to fetch the raw content of the Dockerfile
                response = requests.get(raw_url)
                response.raise_for_status()
                dockerfile_content = response.text

                # Extract image names from the Dockerfile
                images = extract_images_from_dockerfile(dockerfile_content)
                all_images.extend(images)
                print(f"Extracted images: {images}")

        print("\nAll extracted images:")
        for image in all_images:
            print(image)


if __name__ == "__main__":
    # Input is null
    main(None)
    # Input is empty
    # main("")
    # Input is not null or empty
    #input_url = "https://gist.githubusercontent.com/jmelis/c60e61a893248244dc4fa12b946585c4/raw/25d39f67f2405330a6314cad64fac423a171162c/sources.txt"
    #main(input_url)

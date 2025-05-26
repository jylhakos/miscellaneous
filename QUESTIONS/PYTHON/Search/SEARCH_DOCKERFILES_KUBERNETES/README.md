Python Script:

The Python script extract_docker_images.py file searches for all repositories to find all Dockerfile files in each repository and extracts the image names from the FROM statements inside each Dockerfile.

Search for public repositories: 

The search_repositories function uses the GitHub API to search for public repositories based on a query. You can modify the query as needed.

Find Dockerfiles in a repository: 

The find_dockerfiles_in_repo function searches for Dockerfile files inside a given repository using the GitHub search code endpoint.

Extract images from Dockerfile: 

The extract_images_from_dockerfile function uses a regular expression to extract image names from the FROM statements inside a Dockerfile.

Main function: 

The main function orchestrates the process:

  It searches for repositories based on a query.
  The search query in the main function is set to find Python repositories, but you can modify it to fit your needs.
  For each repository, it finds all Dockerfiles.
  It retrieves the content of each Dockerfile and extracts image names from the FROM statements.
  The URL transformation from GitHub to raw GitHub content is done to fetch the raw content of the Dockerfile
  Finally, it prints all the extracted image names in JSON object with the information.

Kubernetes Job:

The deployment.yaml creates a Kubernetes Job to run the Python script.

A ConfigMap is used to store the Python script and mount it as a volume into the job's container.
The job runs the Python script inside a Python 3.8 container.

Linux Shell:

To deploy this on a Kubernetes cluster apply the deployment file by the kubectl command.

  $ kubectl apply -f deployment.yaml
  
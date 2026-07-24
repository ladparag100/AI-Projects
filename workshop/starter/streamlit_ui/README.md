# Deploying the Streamlit UI to Cloud Run

This document provides instructions on how to deploy the Streamlit UI for the AI Creative Studio to Google Cloud Run.

## Prerequisites

1.  **Google Cloud SDK:** Make sure you have the `gcloud` command-line tool installed and configured for your project.
2.  **Docker:** You need Docker installed and running to build the container image.
3.  **Enable APIs:** Ensure the Cloud Build, Artifact Registry, and Cloud Run APIs are enabled for your Google Cloud project. You can enable them with the following commands:

    ```bash
    gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com
    ```

4.  **Creative Director Cloud Run URL:** You need the Cloud Run URL of your deployed "creative director" service.

## Deployment Steps

1.  **Set up environment variables:**

    Replace `[YOUR_PROJECT_ID]` and `[YOUR_REGION]` with your Google Cloud project ID and region.

    ```bash
    export PROJECT_ID=project-8a378124-dc5f-47f4-91a
    export REGION=us-central1
    export REPO_NAME=ai-creative-studio-repo
    export IMAGE_NAME=streamlit-ui
    export IMAGE_TAG=latest
    ```

2.  **Configure gcloud:**

    ```bash
    gcloud config set project $PROJECT_ID
    gcloud config set run/region $REGION
    ```

3.  **Create an Artifact Registry repository:**

    You only need to do this once per project.

    ```bash
    gcloud artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION
    ```

4.  **Build the Docker image:**

    From the `ai-creative-studio/workshop/starter/streamlit_ui` directory, run the following command to build the Docker image and push it to Artifact Registry:

    ```bash
    gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$IMAGE_TAG .
    ```

5.  **Deploy to Cloud Run:**

    Replace `[YOUR_CREATIVE_DIRECTOR_URL]` with the URL of your deployed creative director service.

    ```bash
    gcloud run deploy streamlit-ui 
        --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$IMAGE_TAG 
        --platform=managed 
        --region=$REGION 
        --allow-unauthenticated 
        --set-env-vars="CREATIVE_DIRECTOR_URL=[YOUR_CREATIVE_DIRECTOR_URL]"
    ```
    When prompted, confirm the deployment.

6.  **Access your application:**

    After the deployment is complete, `gcloud` will provide you with the URL to access your Streamlit application.

You have now successfully deployed the Streamlit UI for the AI Creative Studio!

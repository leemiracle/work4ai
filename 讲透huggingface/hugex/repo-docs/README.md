---
title: HugeX Explore
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 3000
---


## Run hugex 

 hugex runs locally and uses Docker to provide runtime environments for coding agents.


# Step by step guide to run hugex locally

Make sure you have Docker installed and running on your machine.

Pull the container image:

```bash
docker pull drbh/codex-universal-explore:dev
```

Next add a `.env` file to the root of the project with the following content:

```env
NODE_ENV=development

GH_TOKEN=github_pat_...
OPENAI_API_KEY=sk-...
```

 Now run the app:

```bash
npm i 
npm run dev
```

navigate to [http://localhost:5173](http://localhost:5173) in your browser.

## Using hugex

Once the app is running you can connect your Github account to see private repos.

 You can choose a repo and add kick off tasks in parallel. The app will create a sandbox Docker container for each task and run the code in that container.

You can customize the container used and envs and secrets passed to the task in the `environment` tab.
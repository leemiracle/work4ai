# Use Custom Skills

DB-GPT supports three ways to use custom skills: create from scratch with the built-in `skill-creator`, upload a zip package, or import via a GitHub link.

## Option 1: Create with skill-creator

`skill-creator` is the built-in meta-skill in DB-GPT, designed to help you create business-specific custom skills. Simply describe your requirements in a conversation, and `skill-creator` handles the entire process from design to packaging.

### Steps

1. Select the `skill-creator` skill in the DB-GPT chat interface.
2. Describe the skill you want to create in natural language, for example: "Create a data analysis skill that reads CSV files and generates visual reports."
3. `skill-creator` will automatically:
   - Analyze your requirements and plan the skill structure
   - Generate `SKILL.md` (including metadata and execution instructions)
   - Create necessary scripts, reference docs, and asset files
   - Validate and package into a distributable `.skill` file

![Create Skill with skill-creator](/img/skill/create_skill.jpg)

For more details on `skill-creator`, see the [skill-creator documentation](./built-in-skills/skill-creator.md).

## Option 2: Upload a Zip Package

If you already have a packaged skill (`.zip` or `.skill` file), you can upload it directly through the DB-GPT Web UI.

### Steps

1. Navigate to the **Skills** page in DB-GPT.

![Skill list page](/img/skill/skill_list.png)

2. Click the upload button and select your local `.zip` or `.skill` file.

![Upload Skill](/img/skill/upload_skill.png)

3. Once uploaded, the skill appears in the list and is ready to use in conversations.

## Option 3: Import via GitHub Link

DB-GPT supports importing skills directly from GitHub repositories — ideal for community or team-shared skills.

### Steps

1. Navigate to the **Skills** page in DB-GPT.
2. Click the GitHub import button and paste the repository URL of the skill.

![Import Skill from GitHub](/img/skill/import_github_skill_.png)

3. The system automatically fetches the repository contents and completes the import. The skill is ready to use once imported.

## Related reading

- [skill-creator](./built-in-skills/skill-creator.md) — Learn about the full capabilities and resources of skill-creator
- [Skills Overview](./introduction.md) — Understand skill definitions, structure, and how they work

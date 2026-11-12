# Contributing to NVAITC APS Project Demos

This guide explains how to contribute to existing projects in this repository.

You can update and improve existing projects. For creating new project folders, please contact your NVIDIA POC.

### 1. Fork the Repository
1. Click the "Fork" button on the main repository page
2. This creates your own copy of the repository

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR-USERNAME/nvaitc-aps-project-demos.git
cd nvaitc-aps-project-demos
```

### 3. Choose a Project to Edit
Browse the existing projects in the `projects/` folder

### 4. Make Your Improvements
1. Navigate to the project you want to update:
   ```bash
   cd projects/existing-project-name
   ```

2. Common improvements you can make:
   - Fix bugs or errors
   - Improve documentation
   - Optimize performance
   - Update dependencies
   - Add better examples
   - Improve code quality

3. Maintain the existing project structure

4. Update the README.md to document your changes:
   ```markdown
   ## Updates
   - [Date] by [Your Name]: Description of changes
   ```

5. Test everything thoroughly!

### 5. Submit Your Work
1. Commit your changes with a clear message:
   ```bash
   git add .
   git commit -m "Update [project-name]: Brief description of changes"
   # Examples:
   # git commit -m "Update explorer-ai: Fix memory leak in agent loop"
   # git commit -m "Update resume-evaluator-ai: Add support for PDF parsing"
   ```

2. Push to your fork:
   ```bash
   git push origin main
   ```

3. Create a Pull Request:
   - Go to your fork on GitHub
   - Click "Contribute" > "Open pull request"
   - Fill out the PR template completely
   - Clearly explain what you changed and why

## Guidelines

### DO:
- ✅ Focus on improving existing projects
- ✅ Maintain backward compatibility when possible
- ✅ Test all changes thoroughly
- ✅ Update documentation to reflect changes
- ✅ Use relative paths
- ✅ Follow the existing code style and conventions
- ✅ Add your changes to the project's README

### DON'T:
- ❌ Create new project folders (contact NVIDIA team if you have a new project idea)
- ❌ Delete or rename existing projects
- ❌ Break existing functionality
- ❌ Upload large files (>50MB)
- ❌ Include sensitive information or credentials
- ❌ Modify projects you're not working on
- ❌ Use absolute paths
- ❌ Submit untested code

## Code Review Process
1. NVIDIA team will review your PR
2. We may request changes or clarifications
3. Once approved, your changes will be merged

## Need Help?
- Study the existing code before making changes
- Open an issue for questions
- Contact your NVIDIA supervisor
- Check the project's existing documentation

## License
By contributing, you agree that your contributions will be licensed under the same license as this repository (Apache 2.0). 

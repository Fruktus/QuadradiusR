# Contributing guidelines
Short summary of practices when developing/contributing to the project.


## Flow
We use standard Gitflow workflow - when beginning work on a new feature,
create a branch for it and when the feature is ready to be merged, create a pull request.

### Branch naming
The branch should be named using following pattern: ```<type>/<issue number>-<issue title separated with hyphens>```
So for example, if the issue is a feature, its number is 6 and title is "Add start button" then the branch name would be ```feature/6-add-start-button```.
The type can be anything you find applicable at the moment, since we do not have solid foundations yet. Most common will be feature or bugfix.

### Pull requests
When making a pull request, please add the [GitHub closing keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) with the issue number, so that it will be linked properly.

We do not enforce the need for Code Review for visual elements, though larger code changes should be verified if possible.


## Styleguide Conventions
We keep the files separated by the folders. All the files should be names in all lowercase, snake_case.

- original_assets - for all the audio and image files from original game only, they should be further separated into lobby and game related ones
- assets - any new assets we made (audio, images, fonts). They should be also separated accordingly.
- prefabs - for all the self contained scenes meant for reusing throughought the project.
- scripts - all the scripts used in nodes
- scenes - all distinct scenes. If major portion of the screen needs changing and does not require animated transitions, consider using scene.

When working with scenes, keep the nodes name in CamelCase, try to always name them accordingly to make it easier to debug and understand.
Do keep the node type in its name, for example when you create VBoxContainer meant for holding players nicknames, you could name it PlayersVBoxContainer.

When working with prefabs, keep in mind following rule - use reference when interacting with child nodes, and signals to interact with parent nodes.
This will allow us easier integration with other elements.

Scripts and prefabs should be further structured into categories, like buttons etc.

### Godot Scripts
Lines from top:
- The class declaration (if applicable)
- The extended node
- One blank line
- Constants
- Variables
- Signals
- Three blank lines

There should be two blank lines between all the functions.

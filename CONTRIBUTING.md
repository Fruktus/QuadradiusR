# Contributing guidelines
Short summary of practices when developing/contributing to the project.


## Flow
We use standard Gitflow workflow - when beginning work on a new feature,
create a branch for it and when the feature is ready to be merged, create a pull request.


## Conventions
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

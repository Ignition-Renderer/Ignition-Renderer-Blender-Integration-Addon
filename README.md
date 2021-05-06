# LavaFrame Blender Integration Addon
As of when I'm writing this, Ignition has no built-in method for editing and creating files. This means that you'd have to learn the [file structure](https://ignitionrenderer.com/docs/#scene-files) to make a scene. This is tedious and can take a while! So, there's gotta be a better method to do it. Well, this is exactly what this is. This is the Blender Integration for Ignition.

# Info
The add-on is currently in closed beta. The only feature at the moment is simple file loading. If you'd like to contribute and help me speed things up, consider switching to the dev branch and doing some PR. Keep in mind that I am working on this when I can and not at all times.
# FAQ
Q: **When is it coming out?**\
A: I don't know. I'm working on it when I can and when I want. I also have school that I need to take care of.\
\
Q: **Will Blender shader node trees work with this add-on?**\
A: No. With the addon, a custom node group called `Ignition Default` will be provided. If that note is not directly connected to the material output, the conversion process will not work and your models will be given no materials.\
\
Q: **What if I don't know Blender?**\
A: Then either learn blender or learn the file structure of a `.ignition` file. If you want to use ignition you don't have a choice here.\
\
Q: **What are your plans?**\
A: File loading, file saving, launching your ignition application to start rendering, and creating a default `ignition` file so you can start working immediately without having to do file manipulation.

# Tomba! Patcher

* You need Python and Pip:
```
pip install -r requirements.txt
python main.py
```

You also need the following tools on the command line:
* https://github.com/Lameguy64/mkpsxiso

# Creating a mod

Each mod is a separate folder into the `mods/` folder. A mod is defined by the `mod.json` file. See the provided example to see how to build one

# Understand the tool

The patcher works in multiple stages:
* Extract
* Patch
* Compilation

## Extract

The extract stage is responsible for the following:
* Dump the game content: This gives us raw files, most of them are compressed and can't be used in this state
* Read LD data, LBA and FLA
* Using those datas, the proper files are then extracted

In the current state, we are left with various files that still need some processing before we can visualize/edit them with modern tools

Each of those files is enriched with suffixes that will be used in the next steps to determine what process should be applied to them.

All the files are then added as tasks in a generic orchestrator. Its job is to run tasks until all of them are finished. Each task can spawn sub-tasks: For example, when a file contains multiple sub-files

This creates a rooted file tasks tree (see https://en.wikipedia.org/wiki/Tree_(graph_theory)).

## Patch

During this step, the patcher loads existing mods using the load order defined in `mods/load_order.json`

Each mod contains a list of patch to apply, those are applied and the patcher remember which files have been modified. It recovers the corresponding task in the tasks tree and reset the task from `finished` to `ready`

When a task is moved in the `ready` state: it also reset it's parent task (ie: the task that spawned it) until it reaches the root.

## Compilation

The orchestrator process again all tasks that are `ready` thus recompiling only files that have been modified to save time.

Finaly, it re-pack the GAM archives and writes any changed data into the FLA and LD game data

# Planned features

* Right now, if a file size changes too much and need more sectors on the game ISO/BIN, thus affecting the LBA, those are not recomputed

* When the extract step is done, the patcher should save the current tasks tree so it can be reloaded between runs and allow the user to skip the extraction or only extract updated files from mods

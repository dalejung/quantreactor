# TODO

## Make cells first class citizens

Instead of the notebook being focus, I want individual cells to be stored separately and referencable on their own. Notebooks would instead be DAGs with the standard notebook being a single pathed graph.

Cells themselves could be referenced by multiple notebooks.

Will be versioned on their own.

They can have relationships to other cells, creating things like reactive chains of execution.

Can have completely different guis.

Not meant to be just a storage mechanism change. But a charge in overall thinking of what a notebook actually is. More like a notebook is just a very simple subset of a bigger type of computation document.

Imagine a cell being a dashboard widget, or an event source that emits events to other cells.

## Push notebook into server

The server should understand the notebook. It will be the source of truth and the notebook gui will be a reflection of that. Something like a reactive chain of cells makes more sense to do in server, especially if you're viewing the same dataset with multiple viewers.

Fixes the long running cell issue.

## more stuff later.



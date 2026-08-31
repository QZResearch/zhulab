---
title: "Coarse-grained model development"
summary: "Deriving coarse-grained interactions bottom-up from atomistic reference data, and mapping the conditions under which they stop being predictive."
icon: "worktree"
weight: 20
---

<!-- To add a figure: drop the image file in this folder, next to index.md,
     then copy the block below out of this comment and delete the /* */ marks.
     `src` is just the filename — no path.

     (The /* */ inside the braces is Hugo's escape: without it Hugo would run
     the shortcode even in here, because shortcodes are expanded before the
     comment is treated as a comment.)

     {{</* figure
         src="cg-mapping.png"
         alt="Atomistic chain mapped onto one bead per residue"
         caption="Mapping an atomistic peptide onto a residue-level representation." */>}}
-->

## Background

A coarse-grained model replaces groups of atoms with single interaction sites
and asks what effective forces should act between them. There are two ways to
answer that. The common one is top-down: pick a functional form, tune its
parameters until the model reproduces a chosen experimental observable, and
ship it. The other is bottom-up: derive the effective interactions from
atomistic simulations of the same system, so that the coarse model inherits its
parameters from a more detailed description rather than from a fitting target.
We work on the second.

The appeal of the bottom-up route is that it is, in principle, systematic —
force matching, relative-entropy minimisation and iterative Boltzmann inversion
all define a well-posed thing to compute. The difficulty is that the object
being computed is not a potential energy but a **free energy**: every degree of
freedom that was integrated out leaves its entropy behind, folded into the
effective interaction. That has a consequence people underestimate. A
free-energy-derived potential belongs to the state point it was derived at.
Change the temperature, the concentration or the composition and there is no
guarantee it still applies.

This is where coarse-grained models quietly fail. A potential matched to
single-chain structure need not reproduce multi-chain thermodynamics —
matching the pair correlation function does not fix the pressure or the phase
behaviour. Implicit solvent makes it sharper still: the solvent entropy is
temperature-dependent, so the effective interactions are too, and temperature is
exactly the axis along which phase diagrams are drawn.

Our interest is in both halves of that problem — deriving the interactions
carefully, and then mapping the boundary of where they hold. A model that is
honest about its own domain of validity is more useful than one that is
slightly more accurate at a single state point.

{{< figure
         src="spatio_temporal.png"
         alt="Atomistic chain mapped onto one bead per residue"
         caption="Schematic illustration of the time and length scale of computational methods utilized for addressing the biomolecular condensates." >}}


<!-- Scaffolding below — replace with real projects and outputs.

## Current projects

- The first project, and who is leading it.

## Selected outputs

Papers, datasets and code from this direction.
-->

---
title: "Machine learning for molecular models"
summary: "Learning representations that carry physics rather than hide it, and using learning to find out which parts of a classical force field are actually wrong."
icon: "wand-magic-sparkles"
weight: 30
---

<!-- Add a figure by dropping the image file in this folder and copying the
     block below out of this comment (delete the /* */ marks).

     {{</* figure
         src="descriptor.png"
         alt="Charge-weighted atom-centred symmetry functions"
         caption="Embedding polarization into the descriptor rather than learning it from geometry alone." */>}}
-->

## Background

A classical force field is a fixed functional form with parameters fitted to a
limited set of reference data, and it fails in characteristic ways on the
properties it was never fitted to. Shear viscosity is a good example: standard
all-atom parameters systematically underestimate the viscosity of alcohols,
because the intermolecular hydrogen bonding that dominates their dynamics is
not what the parameters were tuned against. Partition coefficients are another:
what a molecule does at a water–octanol interface depends on how its charge
distribution responds to the surrounding phase, and a fixed-charge model has
no way to express that.

Machine learning is the obvious lever, and the obvious trap. A neural network
potential can fit almost anything, which means it can also fit the wrong thing
convincingly — reproducing a training set while carrying no transferable
physics and offering no way to see where it will break. Our interest is in the
narrower and more useful version of the idea: **build the physics into the
representation, and use learning where a human fitting by hand would be
guessing.**

One direction is descriptors that encode what the model is missing. Atom-centred
symmetry functions describe a local environment through geometry alone; by
weighting them with the atomic partial charge and averaging them over a
Boltzmann-weighted ensemble of conformers, polarization and conformational
entropy enter the representation explicitly rather than being inferred. Trained
on measured partition coefficients and summed over atomic contributions, that
gives a model that transfers to molecules and datasets it never saw — and one
whose predictions can be read back atom by atom.

The other direction runs the opposite way: use learning to interrogate a
classical model rather than replace it. Across seventy-five organic liquids
spanning nine orders of magnitude in viscosity, feature selection pointed
squarely at hydrogen bonding and molecular topology, and showed that the van
der Waals term — not the torsional one — was the part carrying the error.
Varying that single term systematically was enough to bring the difficult
liquids into line. The lesson generalises: knowing *which* parameter is wrong
is worth more than a black box that is right on average.

Both threads feed the same question that runs through our
[coarse-grained model development]({{< relref "/research/coarse-grained-models" >}}) —
how to build effective interactions that stay predictive away from the
conditions they were derived at, and how to know when they stop.

## Selected outputs

- Q. Zhu *et al.*, "Molecular partition coefficient from machine learning with
  polarization and entropy embedded atom-centered symmetry functions",
  *Phys. Chem. Chem. Phys.* **24** (2022).
  [10.1039/D2CP02648A](https://doi.org/10.1039/D2CP02648A)
- Q. Zhu *et al.*, "Shear viscosity prediction of alcohols, hydrocarbons,
  halogenated, carbonyl, nitrogen-containing, and sulfur compounds using the
  variable force fields", *J. Chem. Phys.* **154**, 074502 (2021).
  [10.1063/5.0038267](https://doi.org/10.1063/5.0038267)

<!-- Scaffolding — replace when there are projects to name.

## Current projects

- The first project, and who is leading it.
-->

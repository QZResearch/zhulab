---
title: "Biomolecular condensates"
summary: "Sequence-resolved simulation of how proteins demix into membraneless compartments, and what tips a liquid droplet towards a solid."
icon: "cloud"
weight: 10
---

<!-- Add a figure by dropping the image file in this folder and copying the
     block below out of this comment (delete the /* */ marks).

     {{</* figure
         src="toc.png"
         alt="Direct-coexistence slab of a condensate"
         caption="A direct-coexistence simulation used to locate the phase boundary." */>}}
-->

## Background

Cells organise a surprising amount of their chemistry without membranes. Stress
granules, nucleoli and a range of other compartments form when proteins and
nucleic acids demix into a dense phase — liquid droplets that concentrate some
molecules and exclude others, assemble in seconds and dissolve just as quickly.
When that process goes wrong, the same droplets can age into the solid,
fibrillar material associated with neurodegenerative disease.

This sits squarely in the blind spot of all-atom simulation. A condensate is
micrometres across and holds thousands of chains, and the demixing plays out
over milliseconds to seconds. Explicit-solvent molecular dynamics, at its best,
follows a handful of chains for microseconds. That gap is not something faster
hardware closes: it is several orders of magnitude in both length and time.

Coarse-graining closes it by discarding what phase behaviour turns out not to
depend on. Most condensate-forming proteins are intrinsically disordered, so
there is no folded structure whose atomic detail has to be preserved — what
sets the phase diagram is the pattern of charged, aromatic and hydrophobic
residues along the sequence. A one-bead-per-residue representation with
implicit solvent keeps exactly that pattern and drops the rest, and the saving
is the difference between watching two chains touch and computing a converged
coexistence curve from a slab of several hundred.

The point of that saving is not speed for its own sake. It is that the
questions become the ones experiments actually ask. How far does swapping
arginine for lysine move the saturation concentration? Which spacing of
aromatic residues holds a droplet together, and which lets it dissolve? What
does a disease-associated mutation do to the phase boundary? Every one of these
is a scan across tens or hundreds of sequence variants — routine at residue
resolution, hopeless atomistically.

What those answers are worth depends on the model underneath them, which is why
this work runs alongside our
[coarse-grained model development]({{< relref "/research/coarse-grained-models" >}}):
a phase diagram computed with a potential that was never tested away from its
reference state point is a prediction with an asterisk on it.

{{< figure
         src="toc.png"
         alt="Direct-coexistence slab of a condensate"
         caption="Approaches used to investigate biomolecular condensates" >}}

<!-- Scaffolding below — replace with real projects and outputs.

## Current projects

- The first project, and who is leading it.

## Selected outputs

Papers, datasets and code from this direction.
-->

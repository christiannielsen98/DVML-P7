# KG Structure Diagram

<a href="https://github.com/christiannielsen98/DVML-P7/blob/main/Code/Illustrations/KG_structure_diagram.jpg" rel="Hello">![Foo](https://raw.githubusercontent.com/christiannielsen98/DVML-P7/main/Code/Illustrations/KG_structure_diagram.jpg)</a>
[Image: KG Structure Diagram]

This is a diagram showcasing the strucutre of our final Yelp knowledge graph, enriched using the Wikidata knowledge graph, created using [miro](miro.com).

The diagram shows the entities as headlines for the different boxes, with square headlines signifying IRIs and trapezoid headlines signifying blank nodes. The yellow and orange boxes are entities originating from the Yelp data while blue boxes are from Wikidata. (FIXME: HVORFOR FARVER? ISÆR NU HVOR DER STÅR WIKIDATA FORAN DE BLÅ)

Inside each box is an overview of the different predicates for each entity. If a predicate exists connecting two different entities, the prediate is instead shown as an arrow between the concerning entities, annotated with the predicate IRI. A special case is the arrow from Business to :\_, which contains many different predicate IRIs. This simply signifies that a Business entity have these predicates connecting it to up to 8 blank nodes.

## [johannes.vc](https://johannes.vc).

## Concept

After a training as someone good at reading and writing, I took the opportunity to use my writings to familiarize myself with Natural Language Processing (NLP) tools and techniques.

## Process

My journey began with conventional NLP methods, clustering texts into topics using LDA, Tf-idf, and exploring word and document vector representations such as Spacy. Eventually, I discovered that transformer-based vectors yielded the best results.

I did make extensive use of Spacy's entity recognition and word vector search (alongside Python's native Regex) to remove potentially identifiable or otherwise inappropriate content.

## Outcome: a Collection of *possible* Essays, Blogs and Articles

Feel free to visit [johannes.vc](https://johannes.vc) to interact with the writings. The 'LLM blog' allows you to propose a topic, which then triggers a semantic search through my work, and rewrites a random selection of what I have written on the topic. It also features a "universe" BERTopic topical modal with a K-Means clustering and t-SNE dimension reduction to visualise the clusters. Selecting a cluster first generates a topic description. You can then generate an article based on the underlying texts. 

## Future Directions

The model is prompted to distinguish my texts from its additions. It doesn't always do this well. It gravitates towards certain formats, losing substance in the process.

This project is a preliminary exploration in presenting writings in a novel, non-linear way. Imagine people interacting with not only books but also people (based on correspondence or social media accounts) for ever... Why even produce a memoir if readers can engage with collections of notes as if they were customised to their interests? Anyway, food for thought!
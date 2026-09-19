I have an important job for you

context: I am building a template/harness that AI agents can follow to create a quantitative research/trade/test platform as a quant dev.

requirements:

1. The book Advances in Financial Machine Learning from Marcos Lopez De Frado is the blueprint of the whole system 
2. The system should be running in C++/C (preferably) for every component backend so it is fast in updates and backtesting. Databases should be considered within our design.
3. The system should support hot swapping and plugging of features, strategies, ML model, market target, displayed information etc.
4. The UI has to be neat, UX has to be handful for quant researchers and quant traders
5. every stored data must be callable and easily accessible but compressed data in database, the book has more detail on it

Flow:

1. Data input should be lossless and quickest api by tick (in microsecond, no delay or lagging), either pre stored data which require no api or api to our database for historical data, or live data which should be stored immediately. Fast in everything, and basically the whole system is constantly running so… yes this is very competitive
2. The data then should be well handled and cleansed without error, stored again (if no change then we wont touch it, update only when changes is there but very unlikely unless change in market target
3. The cleansed data then runs through the feature generation and stored again as either cache or database
4. The features then will be either passed to model learning part, then get backtested or immediately get backtest according to the book through different test (test also might include walk forward etc there are way more in the book
5. I will hope that a template of the feature or strategy part can be provided so quant traders or researchers can easily work on them

Structures:

1. We will be doing A stock but might change to other sectors, then under A stock there are many more sectors which i will want to sectorise them like by industry etc, referencing the world quant brain, so it is like each level we can have the overview or relevant information or calculation etc, a bit abstract here but it is for later to design the best useful tool for the quants

Instructions:\
First, the book will be given, extract every single format and formulas without missing in word. then process each chapters and sub chapters (up to x.x.x.x.x), create a description for each chapters like so, outlining what need to be done, and what need to be cautious. this wil then become a todo checklist. we must strictly follow word by word of what the book is doing so extraction and writing the md outlines the whole template. Ofc we can use the md later to generate everything again, but to keep things simple i will then want templates (this is up to deploy stage which is none of our business) being done following the whole massive file system of mds. This should also follow a good engineering and system design and computer science practice, Evaluation of code and testing is a must. Math wise this system should also be quick but precise without any logic error, no precision loss, no math error. you should also notice and look for any error in the book, IMPORTANT: we must strictly follow the book first and we will design the remaining later. Page by page, word by word, eval checking everything is being done correctly following the book order, which is why we have this task.[@GitHub](plugin://github@openai-curated-remote) create a repo for this project, then start building there

root should have one actual system and one for the instruction md and etc.

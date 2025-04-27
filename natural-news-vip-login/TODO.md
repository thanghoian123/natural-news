# RAG implementation on Write.webseed

### Todo


### In Progress

  Need to create task to enhance the RAG pipeline on write.webseed
-  https://healthrangerstore.slack.com/archives/C06C2PXDP9B/p1743872601304179
Check and expand the input of Enoch-Deepseek for RAG engine to more like 64K tokens.
estimation 6 Hours
- https://healthrangerstore.slack.com/archives/C06C2PXDP9B/p1743882875832879
Add new data from Mike to the Pinecone ingestion queue.
estimation 3 Hours

### Done ✓
-  [x] [RAG-augmented instance of Qwen2.5-32B on AWS](https://app.shortcut.com/cwclabs/story/35351/rag-augmented-instance-of-qwen2-5-32b-on-aws)
    -  [x] Create function to reads all txt files from a given directory

    -  [x] Create function to break down each text in a list of texts into chunks of a maximum size

    -  [x] Create function to generate embeddings for a list of documents.

    -  [x] Create function to generate a short ID based on the content using SHA-256 hash to add Unique IDs to Data

    -  [x] Create function to combine embedding vector and text

    -  [x] Combine documents with their embeddings and metadata.

    -  [x] Create function to upsert data into a Pinecone index.

    -  [x] Download and config BAAI/BGE-M3 model for embedding

    -  [x] Create function to Query the Pinecone index.

    -  [x] Create function to combine RAG to LLMs

    -  [x] Test upsert data to Pinecone database after indexing with API key

    -  [x] Embedding and indexing the 6GB of our core data + 6GB of synth data

    -  [x] Create a new layout for RAG implementation project on write.webseed

    -  [x] Deploy to write.webseed
# Enoch Wellconsumer

### Todo
Mockup UI shown [here](https://3.basecamp.com/4313904/buckets/41013105/todos/8398854030):
- [ ] [Added a settings dropdown menu for Gold and Platinum members to switch between the default and reasoning models.](https://app.shortcut.com/cwclabs/story/35675/added-a-settings-dropdown-menu-for-gold-and-platinum-members-to-switch-between-the-default-and-reasoning-models)
- [ ] [Add view to shows a "unlock" popup message.](https://app.shortcut.com/cwclabs/story/35678/add-view-to-shows-a-unlock-popup-message)

- [ ] [Add dark, light mode](https://app.shortcut.com/cwclabs/story/35030/add-dark-light-mode)
- [ ] [View Profile UI](https://app.shortcut.com/cwclabs/story/35027/view-profile-ui)
- [ ] [Add UI view if there is no exist user found after retrieve API](https://app.shortcut.com/cwclabs/story/35025/add-ui-view-if-there-is-no-exist-user-found-after-retrieve-api)
- [ ] [updated text for platinum members.](https://app.shortcut.com/cwclabs/story/35679/updated-text-for-platinum-members)
- [ ] [Create webhook for shopify to receive when user update their order.](https://app.shortcut.com/cwclabs/story/35316/create-webhook-for-shopify-to-receive-when-user-update-their-order
)
### In Progress

- Record a video to show the implementation have done.

### Done ✓

- [x] [Develop function to check user tier by fetch data from Shopify API](https://app.shortcut.com/cwclabs/story/34894/develop-function-to-check-user-tier-by-fetch-data-from-shopify-api)
- [x] [UI design for Home view](https://app.shortcut.com/cwclabs/story/35230/ui-design-for-home-view)
- [x] [Copy button for chat message](https://app.shortcut.com/cwclabs/story/35026/copy-button-for-chat-message)
- [x] [Develop function to send session login password to user via email](https://app.shortcut.com/cwclabs/story/35325/develop-function-to-send-session-login-password-to-user-via-email)
- [x] [https://app.shortcut.com/cwclabs/story/34897/develop-function-to-send-response-message-of-llm-to-websocket](https://app.shortcut.com/cwclabs/story/34897/develop-function-to-send-response-message-of-llm-to-websocket)
- [x] [Add delete chat UI](https://app.shortcut.com/cwclabs/story/35028/add-delete-chat-ui)
- [x] [Add delete all chat history](https://app.shortcut.com/cwclabs/story/35029/add-delete-all-chat-history) 
- [x] [Regenerate function for chat](https://app.shortcut.com/cwclabs/story/35024/regenerate-function-for-chat)
- [x] [Develop cronjob to reset amount of question per day base on user tier](https://app.shortcut.com/cwclabs/story/35065/develop-cronjob-to-reset-amount-of-question-per-day-base-on-user-tier)
- [X] [Create function to deduct amount of question per day base on user tier](https://app.shortcut.com/cwclabs/story/35064/create-function-to-deduct-amount-of-question-per-day-base-on-user-tier)
- [x] [Develop function to check user tier by Retrieve, check from Active campaign](https://app.shortcut.com/cwclabs/story/34893/develop-function-to-check-user-tier-by-retrieve-check-from-active-campaign)
- [x] [Develop function to retrieve amount spent of user around 3 months for Shopify](https://app.shortcut.com/cwclabs/story/34963/develop-function-to-retrieve-amount-spent-of-user-around-3-months-for-shopify) 
- [x] [UI design for chat page](https://app.shortcut.com/cwclabs/story/34896/ui-design-for-chat-page)
- [x] [UI design for login page](https://app.shortcut.com/cwclabs/story/34895/ui-design-for-login-page)
- [x] [Create database schemas for chat](https://app.shortcut.com/cwclabs/story/34892/create-database-schemas-for-chat) 
- [x] [Create database schemas for user](https://app.shortcut.com/cwclabs/story/34891/create-database-schemas-for-user)
- [x] [Create websocket to receive streaming response of chat message from LLM](https://app.shortcut.com/cwclabs/story/34900/create-websocket-to-receive-streaming-response-of-chat-message-from-llm)
- [x] [Create websocket to receive streaming response of chat message from LLM for Ingredients checker](https://app.shortcut.com/cwclabs/story/34962/create-websocket-to-receive-streaming-response-of-chat-message-from-llm-for-ingredients-checker)

# Continuous Pretraining Qwen2.5-14B
Description:
NEW TASK FOR NEIL: I want you to download all our .txt data files, they contain unstructured text data. I want you to figure out how to run CPT (continuous pre-training) on Qwen2.5-14B, the base model 16-bit FP), using CPT. Note this is NOT an "instruct" model but rather just the base model. See if you can make that happen. The compute should take maybe 4 days on the 8-GPU cluster, something like that. Once you have the CPT output done, then we can use fine-tuning to transform it into an instruct model. Find a good "instruct" SFT data set, or I will also look for one. Please proceed with the CPT task first.


Pending due to Mike's request:
https://healthrangerstore.slack.com/archives/C06C2PXDP9B/p1743299432354889


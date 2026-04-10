# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Trương Quang Lộc
**Nhóm:** 29
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector embedding có hướng gần giống nhau trong không gian vector. Điều đó thường cho thấy hai đoạn văn bản có nội dung hoặc ngữ nghĩa liên quan chặt chẽ.

**Ví dụ HIGH similarity:**
- Sentence A: `Tesla does not pay cash dividends to shareholders.`
- Sentence B: `Tesla has never declared dividends on its common stock.`
- Tại sao tương đồng: Cả hai câu đều truyền đạt cùng một ý về chính sách không chia cổ tức của Tesla.

**Ví dụ LOW similarity:**
- Sentence A: `Gigafactory Texas is located in Austin.`
- Sentence B: `I made coffee before going to class.`
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau, không có liên hệ ngữ nghĩa trực tiếp.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity đo độ giống nhau theo hướng của vector thay vì độ lớn tuyệt đối, nên phù hợp hơn với text embeddings nơi ý nghĩa thường được mã hóa ở hướng biểu diễn. Điều này giúp so sánh ổn định hơn giữa các vector có độ dài khác nhau.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)`  
> *Đáp án:* **23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100 thì số chunk cũng tăng: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lớn hơn giúp giữ lại ngữ cảnh ở ranh giới giữa hai chunk, giảm nguy cơ cắt mất thông tin quan trọng.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Finance

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain tài chính vì đây là loại tài liệu khó, dài và có nhiều số liệu quan trọng nên rất phù hợp để đánh giá chất lượng retrieval. Báo cáo tài chính cũng giúp nhóm kiểm tra rõ hơn tác động của chunking strategy đến độ chính xác của câu trả lời.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | `tsla-20251231.pdf` (Tesla 10-K Annual Report 2025, 169 trang) | SEC EDGAR / Tesla IR | 395,205 | `source`, `company`, `doc_type`, `fiscal_year`, `chunk_index` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | string | `"tsla-20251231.pdf"` | Xác định tài liệu gốc, hỗ trợ filter theo file và delete theo document |
| `company` | string | `"Tesla"` | Giúp filter đúng công ty khi sau này có nhiều tài liệu từ nhiều doanh nghiệp |
| `doc_type` | string | `"10-K Annual Report"` | Phân loại loại báo cáo để truy vấn đúng ngữ cảnh |
| `fiscal_year` | int | `2025` | Tránh trộn số liệu giữa các năm tài chính khác nhau |
| `chunk_index` | int | `42` | Hỗ trợ xác định vị trí chunk trong tài liệu để lấy thêm context xung quanh |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu `tsla-20251231.pdf`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `tsla-20251231.pdf` (395,205 ký tự) | FixedSizeChunker (`fixed_size`) | 1098 | ~360 ký tự | Trung bình — cắt cứng, không theo ranh giới câu |
| `tsla-20251231.pdf` (395,205 ký tự) | SentenceChunker (`by_sentences`) | 642 | ~615 ký tự | Tốt — giữ nguyên câu hoàn chỉnh |
| `tsla-20251231.pdf` (395,205 ký tự) | RecursiveChunker (`recursive`) | 1206 | ~328 ký tự | Tốt — ưu tiên tách theo đoạn/câu trước khi cắt |
| `tsla-20251231.pdf` (395,205 ký tự) | ParagraphChunker (`paragraph`) | 615 | ~800 ký tự | Tốt — giữ nguyên đoạn văn, packing greedy theo `max_chunk_size`; bị ảnh hưởng bởi PDF header noise |

### Strategy Của Tôi

**Loại:** `ParagraphChunker` (custom strategy)

**Mô tả cách hoạt động:**
> ParagraphChunker tách văn bản thành các khối dựa trên ranh giới đoạn văn (blank lines), sau đó greedy-pack các đoạn liền kề lại với nhau cho đến khi tổng độ dài chạm ngưỡng max_chunk_size. Đoạn nào vượt ngưỡng thì fallback tách theo câu. Cách này ưu tiên giữ nguyên ý nghĩa của từng đoạn văn thay vì cắt theo số ký tự cố định hay đơn vị câu.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Báo cáo tài chính 10-K có cấu trúc đoạn rõ ràng — mỗi đoạn thường trình bày một ý hoàn chỉnh (chính sách, rủi ro, số liệu cụ thể). ParagraphChunker giữ nguyên ranh giới đoạn nên mỗi chunk embedding một khái niệm trọn vẹn, tránh cắt đứt giữa luận điểm. Avg chunk size ~800 ký tự cũng lớn hơn các strategy khác, mang nhiều ngữ cảnh hơn cho mỗi lần retrieve.

**Code snippet (nếu custom):**
```python
# Custom idea: split theo paragraph, rồi greedy-pack các paragraph ngắn
# vào cùng một chunk cho đến khi gần chạm max_chunk_size.
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| `tsla-20251231.pdf` | SentenceChunker (best baseline) | 642 | ~615 ký tự | 6.65/10 avg |
| `tsla-20251231.pdf` | **ParagraphChunker (của tôi)** | 615 | ~800 ký tự | 6.00/10 avg |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi — Trương Quang Lộc | `ParagraphChunker` | 6.00 | Giữ nguyên đoạn văn, chunk mang ý nghĩa hoàn chỉnh hơn | PDF header `Tesla, Inc.` tạo noise chunk; Q1 top-1 lệch, Q2 dễ hallucinate HQ, Q3 miss hoàn toàn |
| Nguyễn Bình Thành | `FixedSizeChunker` | 5.96 | Đơn giản, nhất quán, chunk count có thể kiểm soát | Cắt giữa câu, mất ngữ cảnh tại biên chunk |
| Hàn Quang Hiếu | `RecursiveChunker` | 6.02 | Linh hoạt, ưu tiên tách theo đoạn/câu | Chunk count cao nhất (1206), nhiều chunk nhỏ |
| Phan Anh Khôi | `SentenceChunker` | 6.65 | Giữ câu hoàn chỉnh, embedding ngữ nghĩa chính xác hơn | Chunk count thấp nhất, câu dài vẫn có thể mang nhiều ý |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> `SentenceChunker` cho retrieval score cao nhất trong nhóm (6.65/10) trên domain tài chính. Với tài liệu 10-K, nhiều thông tin quan trọng nằm gọn trong các câu hoàn chỉnh, nên việc giữ nguyên câu giúp embedding nắm ngữ nghĩa tốt hơn và giảm hiện tượng mất ý khi retrieve.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi tách câu bằng regex theo dấu kết câu như `.`, `!`, `?` kết hợp khoảng trắng hoặc xuống dòng, sau đó `strip()` và loại bỏ phần rỗng để tránh tạo chunk rác. Cuối cùng, các câu được gom lại theo `max_sentences_per_chunk` để tạo các chunk có cấu trúc ổn định và dễ kiểm soát hơn.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Tôi implement theo hướng đệ quy: trước tiên thử tách bằng separator lớn như `\n\n`, `\n`, rồi nhỏ dần đến `. `, khoảng trắng và cuối cùng là hard slicing. Base case là text rỗng, text đã ngắn hơn `chunk_size`, hoặc không còn separator nào khả dụng thì cắt cứng theo kích thước tối đa.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi document được chuẩn hóa thành một record gồm `id`, `content`, `metadata` và `embedding`, sau đó lưu vào `_store` trong chế độ in-memory nếu không có ChromaDB. Khi search, tôi embed câu hỏi, tính similarity bằng dot product với tất cả vector đã lưu, rồi sắp xếp giảm dần theo `score` để lấy top-k.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` sẽ lọc metadata trước rồi mới chạy similarity search trên tập con, giúp giảm nhiễu và tăng precision khi query có phạm vi cụ thể. `delete_document` xóa tất cả record có `metadata['doc_id'] == doc_id`, đồng thời thử xóa phía Chroma nếu backend này đang được bật.

### KnowledgeBaseAgent

**`answer`** — approach:
> Hàm `answer()` lấy top-k chunks liên quan từ store, sau đó ghép chúng thành một `Context` block có đánh số và score để làm bằng chứng cho prompt. Prompt được xây theo dạng instruction + context + question, yêu cầu model chỉ trả lời dựa trên context và nói rõ nếu thông tin chưa đủ, nhằm giảm hallucination và bám sát RAG pattern.

### Test Results

```text
===================================== 42 passed in 1.05s =====================================
```

**Số tests pass:** **42 / 42**

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Tesla had 134,785 employees as of December 31, 2025 | Tesla's global workforce numbered 134,785 people at year-end | high | 0.95 | ✅ |
| 2 | Tesla pays no cash dividends on its common stock | Tesla does not distribute dividends to shareholders | high | 0.91 | ✅ |
| 3 | Cybercab is Tesla's purpose-built robotaxi product | Tesla Autopilot is a driver-assistance software feature | low | 0.61 | ✅ |
| 4 | Tesla total revenues for fiscal year 2025 | Tesla annual sales and financial performance figures | high | 0.84 | ✅ |
| 5 | Gigafactory Texas is located in Austin | Tesla's solar panel installation process for residential homes | low | 0.38 | ✅ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Cặp gây bất ngờ nhất là `Cybercab` và `Autopilot` vì dù đều liên quan đến Tesla và autonomous driving nhưng score không cao như dự đoán ban đầu. Điều này cho thấy embeddings không chỉ nhìn từ khóa chung mà còn phân biệt khá tốt vai trò, loại thực thể và ngữ cảnh cụ thể của từng câu.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân với strategy `ParagraphChunker`. Dựa trên tổng hợp benchmark của nhóm, strategy này đạt khoảng **6.0/10**, chủ yếu vì chunk giữ được paragraph hoàn chỉnh nhưng vẫn bị ảnh hưởng bởi noise từ header PDF.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | How many employees did Tesla have as of end of 2025? | As of December 31, 2025, Tesla had 134,785 employees worldwide. |
| 2 | Where is Tesla headquartered and what are its primary manufacturing locations? | Tesla is headquartered in Austin, Texas. Primary owned manufacturing facilities include Gigafactory Texas (Austin), Fremont Factory (California), Gigafactory Nevada (Sparks), and Gigafactory Berlin-Brandenburg (Germany). Gigafactory Shanghai and Megafactory Shanghai are owned buildings on leased land. |
| 3 | Does Tesla pay dividends to its shareholders? | Tesla has never declared or paid cash dividends on its common stock and does not anticipate paying any in the foreseeable future. |
| 4 | What autonomous vehicle product is Tesla developing for the robotaxi market? | Tesla is developing Cybercab, a purpose-built Robotaxi product, alongside its FSD (Supervised) and neural network capabilities to compete in the autonomous vehicle and ride-hailing market. |
| 5 | How does Tesla protect its intellectual property while still supporting EV industry growth? | Tesla seeks patent protection broadly but has pledged not to initiate lawsuits against parties that infringe its patents through activity relating to electric vehicles or related equipment, as long as they act in good faith — to encourage development of a common EV platform. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tesla employees end of 2025? | Patent policy chunk — không liên quan đến headcount | 0.6278 | Partial | Answer đúng (134,785) dù top-1 lệch; số liệu nằm ở chunk khác trong context. |
| 2 | Tesla HQ & primary manufacturing locations? | "Tesla, Inc." (PDF header noise) — không có thông tin HQ | 0.6139 | No | Hallucinate HQ là "Palo Alto, California"; danh sách factories đúng nhờ top-2. |
| 3 | Tesla pay dividends? | "Tesla, Inc." (PDF header noise) | 0.5976 | No | Top-3 không có chunk về dividend policy. AI: "context does not contain information." |
| 4 | Tesla autonomous vehicle for robotaxi market? | "Our Robotaxi business... will include Cybercab, our purpose-built autonomous vehicle." | 0.6709 | Yes | Tesla đang phát triển Cybercab — robotaxi mục đích chuyên dụng. |
| 5 | Tesla IP protection & EV growth? | "irrevocably pledged that we will not initiate a lawsuit... relating to electric vehicles..." | 0.6411 | Yes | Tesla bảo vệ IP qua patent, cam kết không kiện bên vi phạm bằng sáng chế EV miễn họ hành động thiện chí. |

**Bao nhiêu queries trả về chunk relevant trong top-3?**
3/5 (Q2, Q3 miss do noise chunk)

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được từ các bạn rằng với tài liệu tài chính dài như 10-K, `SentenceChunker` thường cho kết quả retrieval ổn định hơn mong đợi vì nhiều số liệu quan trọng nằm gọn trong một câu. Việc giữ nguyên câu đôi khi hiệu quả hơn việc cố giữ cả paragraph nếu paragraph đó bị lẫn header hoặc nhiều ý không liên quan.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Tôi rút ra rằng chất lượng retrieval không chỉ phụ thuộc vào code chunking mà còn phụ thuộc mạnh vào bước làm sạch dữ liệu đầu vào. Những nhóm xử lý tốt header/footer noise, metadata và benchmark queries thường có kết quả nhất quán hơn rất nhiều.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Nếu làm lại, tôi sẽ preprocess PDF kỹ hơn để loại bỏ header/footer như `Tesla, Inc.` trước khi chunking, vì đây là nguồn noise rõ ràng trong kết quả của tôi. Tôi cũng sẽ thêm metadata như `section`, `page`, hoặc `item` để filter chính xác hơn cho các câu hỏi về employee count, dividends và facilities.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 13 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 6 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **84 / 100** |

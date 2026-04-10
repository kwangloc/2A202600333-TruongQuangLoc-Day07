# Group Report Suggestion — Lab 7: Embedding & Vector Store

> **Note:** This is a **sample group report** with **illustrative / fake benchmark results** for drafting and discussion. Update names and any details before submission.

**Nhóm:** Nhóm 7 — Retrieval Explorers  
**Thành viên:** Trương Quang Lộc, Nguyễn Văn A, Trần Thị B  
**Ngày:** 10/04/2026

---

## 1. Group Topic and Goal

Nhóm chọn chủ đề **trợ lý tri thức cho thương mại điện tử** với các tài liệu về đơn hàng, thanh toán, vận chuyển, đổi trả và chăm sóc khách hàng. Mục tiêu là so sánh các chiến lược chunking khác nhau để xem chiến lược nào giúp retrieval ổn định hơn khi trả lời câu hỏi thực tế của khách hàng và nhân viên vận hành trong hệ thống e-commerce.

Nhóm tập trung vào ba yếu tố chính:
- **Chunk coherence**: chunk có giữ được ý trọn vẹn không
- **Retrieval precision**: top-k có chứa đoạn thật sự liên quan không
- **Metadata utility**: filter có giúp giảm nhiễu không

---

## 2. Document Selection

### Domain & Rationale

Nhóm chọn domain **e-commerce operations + customer support** vì đây là một bối cảnh rất thực tế cho RAG: khách hàng thường hỏi về trạng thái đơn hàng, chính sách đổi trả, thanh toán, voucher và thời gian giao hàng. Bộ dữ liệu được thiết kế để phản ánh cả kiến thức vận hành nội bộ lẫn nội dung hỗ trợ khách hàng, nên phù hợp để đánh giá chất lượng retrieval và giá trị của metadata filtering.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | `order_faq.md` | Tài liệu nhóm biên soạn | 2100 | `category=orders`, `language=vi`, `audience=customer` |
| 2 | `shipping_policy.md` | Tài liệu nhóm biên soạn | 1850 | `category=shipping`, `language=vi`, `audience=customer` |
| 3 | `return_refund_policy.md` | Tài liệu nhóm biên soạn | 2300 | `category=returns`, `language=vi`, `audience=customer` |
| 4 | `payment_troubleshooting.txt` | Tài liệu nhóm biên soạn | 1700 | `category=payment`, `language=vi`, `audience=support` |
| 5 | `seller_operations_guide.md` | Tài liệu nhóm biên soạn | 2600 | `category=operations`, `language=vi`, `audience=internal` |
| 6 | `promotion_rules.md` | Tài liệu nhóm biên soạn | 1600 | `category=promotion`, `language=vi`, `audience=customer` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ | Vai trò trong retrieval |
|----------------|------|-------|--------------------------|
| `category` | string | `orders`, `shipping`, `returns` | Giúp giới hạn truy xuất theo đúng nghiệp vụ khách đang hỏi |
| `language` | string | `vi` | Giúp hệ thống ưu tiên tài liệu tiếng Việt cho người dùng nội địa |
| `audience` | string | `customer`, `support`, `internal` | Tránh việc khách hàng nhìn thấy hướng dẫn nội bộ hoặc quy trình backend |

**Kết luận:** Trong quá trình benchmark, `category` và `audience` là hai metadata hữu ích nhất. Chúng làm giảm nhiễu rõ rệt, nhất là khi cần tách câu trả lời dành cho khách hàng với hướng dẫn chỉ dành cho bộ phận hỗ trợ.

---

## 3. Strategy Design and Comparison

### Baseline Comparison

Nhóm sử dụng `ChunkingStrategyComparator().compare()` với `chunk_size=200` trên ba tài liệu tiêu biểu.

| Tài liệu | Strategy | Chunk Count | Avg Length | Nhận xét nhanh |
|---------|----------|-------------|------------|----------------|
| `order_faq.md` | Fixed Size | 10 | 198.40 | Gọn nhưng đôi lúc cắt giữa câu hỏi và câu trả lời |
| `order_faq.md` | Sentence | 7 | 236.80 | Dễ đọc, hợp nội dung FAQ |
| `order_faq.md` | Recursive | 12 | 151.30 | Cân bằng tốt giữa FAQ và giải thích dài |
| `return_refund_policy.md` | Fixed Size | 12 | 191.75 | Ổn định nhưng có đoạn bị mất ý |
| `return_refund_policy.md` | Sentence | 9 | 224.10 | Dễ kiểm tra thủ công |
| `return_refund_policy.md` | Recursive | 16 | 129.55 | Tốt nhất về coherence |
| `seller_operations_guide.md` | Fixed Size | 13 | 199.15 | Tốt cho baseline đơn giản |
| `seller_operations_guide.md` | Sentence | 10 | 210.45 | Giữ câu rõ ràng |
| `seller_operations_guide.md` | Recursive | 19 | 118.20 | Linh hoạt nhất với tài liệu nhiều mục |

### Member Strategies

| Thành viên | Strategy | Cấu hình | Lý do chọn |
|-----------|----------|----------|------------|
| Trương Quang Lộc | `RecursiveChunker` | `chunk_size=200` | Phù hợp tài liệu e-commerce dài như policy và guide nội bộ |
| Nguyễn Văn A | `SentenceChunker` | `max_sentences_per_chunk=2` | Dễ đọc, phù hợp FAQ, hướng dẫn đổi trả và shipping |
| Trần Thị B | `FixedSizeChunker` | `chunk_size=200, overlap=30` | Dễ triển khai, cho baseline ổn định để so sánh |

### Group Comparison Summary

| Strategy | Điểm mạnh | Điểm yếu | Điểm nhóm đánh giá (/10) |
|----------|-----------|----------|---------------------------|
| Fixed Size | Đơn giản, dễ kiểm soát độ dài | Dễ cắt mất ngữ cảnh ở giữa câu | 6.5 |
| Sentence | Chunk dễ đọc, tự nhiên | Có thể không đều kích thước, kém hiệu quả với đoạn dài | 7.5 |
| Recursive | Cân bằng giữa cấu trúc và độ dài | Tạo nhiều chunk hơn, cần tuning tốt | 8.5 |

**Kết luận của nhóm:** `RecursiveChunker` là chiến lược tốt nhất cho bộ dữ liệu e-commerce này. Nó không phải lúc nào cũng có top-1 chính xác nhất, nhưng thường cho **top-3 hữu ích hơn** và giữ được ý nghĩa tốt hơn trong các tài liệu policy, vận hành và xử lý sự cố thanh toán.

---

## 4. Benchmark Queries and Gold Answers

Nhóm thống nhất **5 benchmark queries** để mọi thành viên chạy trên cùng bộ dữ liệu.

| # | Query | Gold Answer | Chunk nên chứa thông tin |
|---|-------|-------------|--------------------------|
| 1 | Đơn hàng đã thanh toán thì bao lâu được giao? | Đơn hàng thường được xử lý trong 24 giờ và giao trong 2–5 ngày tùy khu vực. | `shipping_policy.md` |
| 2 | Khi nào khách được hoàn tiền? | Khách được hoàn tiền khi đơn bị hủy hợp lệ, hàng lỗi, hoặc trả hàng đúng chính sách. | `return_refund_policy.md` |
| 3 | Nếu thanh toán thất bại thì nên làm gì? | Kiểm tra số dư, phương thức thanh toán, thử lại hoặc liên hệ hỗ trợ nếu lỗi tiếp diễn. | `payment_troubleshooting.txt` |
| 4 | Voucher không áp dụng được là vì sao? | Có thể do chưa đạt giá trị tối thiểu, sai ngành hàng, hết hạn, hoặc hết lượt sử dụng. | `promotion_rules.md` |
| 5 | Hướng dẫn nội bộ cho nhân viên xử lý đơn giao thất bại là gì? | Nhân viên cần kiểm tra trạng thái vận đơn, liên hệ đối tác giao hàng và cập nhật ticket nội bộ. | `seller_operations_guide.md` |

> Query #5 là truy vấn mà **metadata filtering** theo `audience=internal` đặc biệt hữu ích.

---

## 5. Benchmark Results by Group Members

> The values below are **sample benchmark results** for reporting format and discussion.

### Member 1 — Trương Quang Lộc (`RecursiveChunker`)

| Query # | Top-1 Relevant? | Top-3 Relevant? | Notes |
|---------|------------------|------------------|-------|
| 1 | Yes | Yes | Retrieved vector store concept clearly |
| 2 | Yes | Yes | Good grounding with RAG description |
| 3 | Partly | Yes | Best evidence appeared in top-2 |
| 4 | No | Yes | Support playbook appeared in top-3 |
| 5 | Yes | Yes | Metadata filter improved accuracy strongly |

**Precision summary:** 4/5 top-1 relevant, 5/5 top-3 relevant

### Member 2 — Nguyễn Văn A (`SentenceChunker`)

| Query # | Top-1 Relevant? | Top-3 Relevant? | Notes |
|---------|------------------|------------------|-------|
| 1 | Yes | Yes | Strong on short conceptual questions |
| 2 | Yes | Yes | Chunks were easy to inspect manually |
| 3 | Yes | Yes | Natural sentence boundaries helped |
| 4 | Partly | Yes | Retrieved partial answer without full escalation detail |
| 5 | No | Yes | Needed filter to become reliable |

**Precision summary:** 3.5/5 top-1 relevant, 5/5 top-3 relevant

### Member 3 — Trần Thị B (`FixedSizeChunker`)

| Query # | Top-1 Relevant? | Top-3 Relevant? | Notes |
|---------|------------------|------------------|-------|
| 1 | Partly | Yes | Found keyword match but context was incomplete |
| 2 | Yes | Yes | Worked well when keywords were explicit |
| 3 | No | Yes | Overlap helped, but top result still lacked full explanation |
| 4 | No | Partly | One chunk cut the support instruction awkwardly |
| 5 | No | Yes | Filtered search improved it, but baseline was noisy |

**Precision summary:** 2/5 top-1 relevant, 4/5 top-3 relevant

---

## 6. Failure Analysis

### Example failure case

**Query:** `Voucher không áp dụng được là vì sao?`

**Observed issue:** Một số lần top-1 result không phải `promotion_rules.md`, mà lại là tài liệu về thanh toán hoặc đơn hàng do các từ chung như “điều kiện”, “áp dụng”, hoặc “giới hạn” xuất hiện ở nhiều nơi.

**Nguyên nhân có thể:**
- Query chứa ý nghĩa liên quan đến promotion nhưng mock embedding không hiểu ngữ cảnh nghiệp vụ đủ sâu
- Chunk quá ngắn hoặc không giữ nguyên phần mô tả điều kiện sử dụng voucher
- Chưa dùng filter theo `category=promotion`

**Đề xuất cải thiện:**
- Thêm metadata filter theo `category=promotion`
- Dùng embedder thật thay cho `_mock_embed`
- Tối ưu chunking để điều kiện voucher và ngoại lệ nằm trong cùng một chunk

### Another failure pattern

**Query:** `Hướng dẫn nội bộ cho nhân viên xử lý đơn giao thất bại là gì?`

**Observed issue:** Nếu không filter theo `audience=internal`, hệ thống có thể trả về chính sách giao hàng dành cho khách hàng thay vì hướng dẫn nội bộ cho nhân viên vận hành. Điều này cho thấy metadata filtering rất quan trọng trong domain thương mại điện tử, nơi có nhiều nhóm người dùng khác nhau.

---

## 7. Lessons Learned

### What the group learned

1. **Chunking matters as much as embeddings.**  
   Cùng một bộ tài liệu nhưng thay đổi chunking strategy có thể làm khác rõ rệt top-3 results.

2. **Metadata is not optional.**  
   Với truy vấn theo ngôn ngữ hoặc domain cụ thể, filter metadata giúp tăng precision đáng kể.

3. **Top-3 is often more informative than top-1.**  
   Một số truy vấn có top-1 chưa tốt, nhưng top-2 hoặc top-3 vẫn chứa evidence quan trọng để agent trả lời.

4. **Mock embeddings are useful for logic tests, not semantic evaluation.**  
   `_mock_embed` rất phù hợp để kiểm thử code và pipeline, nhưng không nên xem là thước đo cuối cùng cho chất lượng retrieval thực tế.

### If we did this again

Nếu làm lại, nhóm sẽ:
- bổ sung thêm tài liệu thực tế hơn về đơn hàng, logistics, đổi trả và khiếu nại khách hàng
- thêm metadata như `shop_region`, `seller_type`, và `last_updated`
- dùng local embedding model thật để benchmark retrieval công bằng hơn
- log chi tiết top-3 chunks cho mọi query để phân tích failure case tốt hơn

---

## 8. Final Group Conclusion

Nhóm kết luận rằng **retrieval quality là kết quả của sự kết hợp giữa data quality, chunking strategy, metadata design và evaluation query design**. Trong domain thương mại điện tử, `RecursiveChunker` là lựa chọn mặc định tốt nhất cho bộ tài liệu hỗn hợp như policy, FAQ và guide nội bộ, còn metadata filtering là yếu tố giúp tăng precision rõ rệt ở các truy vấn có ràng buộc về đối tượng người dùng hoặc nghiệp vụ.

Dù kết quả benchmark trong bài còn chịu ảnh hưởng của `_mock_embed`, nhóm vẫn rút ra được bài học rõ ràng: **RAG trong thương mại điện tử không chỉ là gắn vector store vào LLM, mà là thiết kế cẩn thận toàn bộ pipeline retrieval để trả lời đúng, an toàn và phù hợp ngữ cảnh người dùng.**

# Pydantic-AI ImageUrl Bug Report

## **Issue Summary**
`ImageUrl` objects with `force_download=True` are not being downloaded locally in OpenAI models, causing failures when URLs are inaccessible to OpenAI servers (e.g., localhost URLs in development).

## **Bug Details**
**Affected Version:** pydantic-ai 1.0.9 (latest)  
**Affected Models:** OpenAI ChatCompletion and Responses API  
**Location:** `/pydantic_ai_slim/pydantic_ai/models/openai.py`

## **Root Cause**
`ImageUrl` handling is inconsistent with other URL types:

**❌ ImageUrl (Lines 1408-1411):**
```python
elif isinstance(item, ImageUrl):
    content.append(
        responses.ResponseInputImageParam(image_url=item.url, type='input_image', detail='auto')
    )
```

**✅ AudioUrl/DocumentUrl (Lines 1412-1419):**
```python
elif isinstance(item, AudioUrl):
    downloaded_item = await download_item(item, data_format='base64_uri', type_format='extension')
    content.append(
        responses.ResponseInputFileParam(
            type='input_file', 
            file_data=downloaded_item['data'],
            filename=f'filename.{downloaded_item["data_type"]}',
        )
```

## **Evidence**
**Error Message:**
```
ModelHTTPError: status_code: 400, model_name: gpt-4o, 
body: {'message': 'Error while downloading http://localhost:8000/...', 
       'type': 'invalid_request_error', 'code': 'invalid_image_url'}
```

**Expected Behavior:** `ImageUrl(url="localhost:8000/...", force_download=True)` should download locally and send binary data to OpenAI.

**Actual Behavior:** URL sent directly to OpenAI, which fails for localhost/inaccessible URLs.

## **Impact**
- Breaks development workflows using localhost URLs
- `force_download=True` parameter is ignored for images
- Inconsistent behavior across URL types

## **Proposed Fix**

**Replace the ImageUrl handling in both locations** (ChatCompletion API ~line 755 and Responses API ~line 1408) with logic that mirrors AudioUrl/DocumentUrl:

```python
elif isinstance(item, ImageUrl):
    # Check if we should download locally (force_download=True or inaccessible URL)
    if item.force_download or _should_download_url(item.url):
        # Download the image locally and send as binary data
        downloaded_item = await download_item(item, data_format='base64_uri', type_format='extension')
        content.append(
            responses.ResponseInputFileParam(
                type='input_file',
                file_data=downloaded_item['data'],
                filename=f'filename.{downloaded_item["data_type"]}',
            )
        )
    else:
        # Use direct URL (current behavior for public URLs)
        content.append(
            responses.ResponseInputImageParam(image_url=item.url, type='input_image', detail='auto')
        )
```

**Additional Helper Function Needed:**
```python
def _should_download_url(url: str) -> bool:
    """Check if URL should be downloaded locally (inaccessible to OpenAI)."""
    return any(host in url for host in ['localhost', '127.0.0.1', '0.0.0.0'])
```

**Key Changes:**
1. **Add URL accessibility check** - Detect localhost/private URLs
2. **Respect force_download flag** - Actually check `item.force_download` 
3. **Use download_item()** - Same function AudioUrl/DocumentUrl use
4. **Binary fallback** - Send as `ResponseInputFileParam` when downloaded locally
5. **Maintain backwards compatibility** - Keep URL-based approach for public URLs

**Benefits:**
- **Development**: localhost URLs get downloaded locally → binary data sent to OpenAI ✅  
- **Production**: Public URLs sent directly → OpenAI downloads them ✅
- **Consistent**: Same pattern as AudioUrl/DocumentUrl ✅
- **Backwards Compatible**: Existing code keeps working ✅

## **Investigation Notes**
- Bug confirmed in both ChatCompletion API (lines 755-757) and Responses API (lines 1408-1411)
- `AudioUrl` and `DocumentUrl` properly use `download_item()` function
- `ImageUrl` bypasses download mechanism entirely
- Same issue exists across multiple locations in openai.py
- Affects our Story Sprout image generation workflow in development

## **Status**
- **Discovered:** 2025-01-19
- **Versions Tested:** 1.0.4, 1.0.9
- **Workaround:** Use BinaryContent instead of ImageUrl for localhost URLs
- **Upstream Issue:** Ready to report to pydantic-ai GitHub

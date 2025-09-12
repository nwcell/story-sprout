# Pydantic Memory

##



ok, let's turn this into a serialize/deserialize helper for conversations.  make it super compact.  strictly follow the format used by pydantic ai (refer to the docs AND the source code here)

make it a class that has a helper function of offloading/onloading of binaries from messages

workflow
default class saves a json file & raw assets to a tmp dir
dev overrides get/set for artifacts
dev overrides get/create_or_append for conversation
dev uses this as a wrapper function to handle messages/conversations w/ pydantic

### Process
```python
from pydantic_ai_memory import MemoryHelper, Artifact
from .local_system import load_artifact, save_artifact

@dataclass
class CashedContent:
    key: UUID =
    content: BinaryContent

class MemoryHelper(MemoryHelper):
    def cache_content(self, content: BinaryContent) -> CashedContent:
        key = uuid()
        save_artifact(key, content.data)
        content.data = None
        return CashedContent(key=key, content=content)

    def hydrate_content(self, content: CashedContent) -> BinaryContent:
        content.data = load_artifact(content.key)
        return content



agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')
result = agent.run_sync('make a pic.')

mem_help = MemoryHelper()

offloaded = result.all_messages()


```

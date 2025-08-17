from pathlib import Path
from unittest import TestCase
from app.embed import embed_text, embed_text_bert
from app.snippets import SnippetSourceFile
from app.vector import SklearnVectorStore

class TestEmbed(TestCase):

    def test_embed_text(self):
        text = "foobar"
        vec = embed_text(text)
        # array.ndim
        import ipdb; ipdb.set_trace()
        print(vec)        

    def test_embed_text_bert(self):
        text = "foobar"
        vec = embed_text_bert(text)
        # array.ndim
        print(vec)
    
    def test_emebed_snippet(self):
        # import ipdb; ipdb.set_trace()
        snippet_source = SnippetSourceFile(Path(__file__).parent.absolute()/"gist.md")
        store = SklearnVectorStore()
        from asgiref.sync import async_to_sync
        snippets = async_to_sync(snippet_source.get_snippets)()
        for i, snippet in enumerate(snippets):
            # print(f"Snippet number: {i}")
            # import ipdb; ipdb.set_trace()
            vec = embed_text_bert(str(snippet))
            # print(vec.ndim)
            store.add(vec, snippet)
        store.fit()

if __name__ == "__main__":
    TestEmbed().test_emebed_snippet()


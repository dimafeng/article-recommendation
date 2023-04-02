from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

class Summarizer():
    def __init__(self):
        model = "facebook/bart-large-cnn"
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model)
        self.summarizer = pipeline("summarization", model=model)

    def __summarize_long_text(self, long_text, max_length=1024):
        # initialize T5 model and tokenizer
    
        # split the long text into smaller segments
        text_segments = [long_text[i:i+max_length] for i in range(0, len(long_text), max_length)]

        # generate summaries for each segment and concatenate them
        summary = ''
        for segment in text_segments:
            input_ids = self.tokenizer.encode('summarize: ' + segment, return_tensors='pt', max_length=max_length, truncation=True)
            output = self.model.generate(input_ids)
            summary += self.tokenizer.decode(output[0], skip_special_tokens=True) + ' '

        return summary

    def summarize(self, text):
        try:
            if text is None or len(text) == 0:
                return None
            
            if len(text) < 250:
                return text

            summary = text
            if len(text) > 1024:
                summary = self.__summarize_long_text(text)

            if len(summary) < 250:
                return summary

            return self.summarizer(summary, max_length=250, min_length=60, do_sample=False)[0].get('summary_text')
        except Exception as e:
            print(e)
            return None
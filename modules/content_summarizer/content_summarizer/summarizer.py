from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Summarizer():
    MAX_LENGTH = 1024
    MAX_SUMMARY_LENGTH = 350

    def __init__(self):
        model = "facebook/bart-large-cnn"
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model)

    def __summarize_long_text(self, long_text):
        # Split the long text into smaller segments
        text_segments = [long_text[i:i+self.MAX_LENGTH] for i in range(0, len(long_text), self.MAX_LENGTH)]

        # Generate summaries for each segment and concatenate them
        summary = ''
        for segment in text_segments:
            input_ids = self.tokenizer.encode('summarize: ' + segment, return_tensors='pt', max_length=self.MAX_LENGTH, truncation=True)
            output = self.model.generate(input_ids)
            summary += self.tokenizer.decode(output[0], skip_special_tokens=True) + ' '

        return summary

    def summarize(self, text):
        """
        Summarize input text.

        Args:
            text (str): Input text to be summarized.

        Returns:
            str: Summarized text.
        """
        try:
            if text is None or len(text) == 0:
                return None
            
            if len(text) < self.MAX_SUMMARY_LENGTH:
                return text

            summary = text
            step = 0
            while len(summary) > self.MAX_SUMMARY_LENGTH:
                print(f'Summarizing (step {step} - length {len(summary)})...')
                summary = self.__summarize_long_text(summary)
                
                if step > 3:
                    return None
                step += 1

            return summary
        except Exception as e:
            print(e)
            return None
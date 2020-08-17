
from deep_translator.constants import BASE_URLS, GOOGLE_LANGUAGES_TO_CODES
from deep_translator.exceptions import NotValidPayload, TranslationNotFound, LanguageNotSupportedException
from deep_translator.parent import BaseTranslator
import requests


class MyMemoryTranslator(BaseTranslator):
    """
    class that uses google translate to translate texts
    """
    _languages = GOOGLE_LANGUAGES_TO_CODES
    supported_languages = list(_languages.keys())

    def __init__(self, source="auto", target="en", **kwargs):
        """
        @param source: source language to translate from
        @param target: target language to translate to
        """
        self.__base_url = BASE_URLS.get("MYMEMORY")
        if self.is_language_supported(source, target):
            self._source, self._target = self._map_language_to_code(source.lower(), target.lower())
            self._source = self._source if self._source != 'auto' else 'Lao'

        print(self._source, self._target)
        self.email = kwargs.get('email', None)
        super(MyMemoryTranslator, self).__init__(base_url=self.__base_url,
                                                 source=self._source,
                                                 target=self._target,
                                                 payload_key='q',
                                                 langpair='{}|{}'.format(self._source, self._target))

    @staticmethod
    def get_supported_languages(as_dict=False):
        return MyMemoryTranslator.supported_languages if not as_dict else MyMemoryTranslator._languages

    def _map_language_to_code(self, *languages):
        """

        @param language: type of language
        @return: mapped value of the language or raise an exception if the language is not supported
        """
        for language in languages:
            if language in self._languages.values() or language == 'auto':
                yield language
            elif language in self._languages.keys():
                yield self._languages[language]
            else:
                raise LanguageNotSupportedException(language)

    def is_language_supported(self, *languages):
        for lang in languages:
            if lang != 'auto' and lang not in self._languages.keys():
                if lang != 'auto' and lang not in self._languages.values():
                    raise LanguageNotSupportedException(lang)
        return True

    def translate(self, text, return_all=False, **kwargs):
        """
        main function that uses google translate to translate a text
        @param text: desired text to translate
        @param return_all: set True to return all synonyms
        @return: str: translated text
        """

        if self._validate_payload(text):
            text = text.strip()

            if self.payload_key:
                self._url_params[self.payload_key] = text
            if self.email:
                self._url_params['de'] = self.email

            response = requests.get(self.__base_url,
                                    params=self._url_params,
                                    headers=self.headers)
            data = response.json()
            if not data:
                TranslationNotFound(text)

            translation = data.get('responseData').get('translatedText')
            if translation:
                return translation

            elif not translation:
                all_matches = data.get('matches')
                matches = (match['translation'] for match in all_matches)
                next_match = next(matches)
                return next_match if not return_all else list(all_matches)

    def translate_sentences(self, sentences=None, **kwargs):
        """
        translate many sentences together. This makes sense if you have sentences with different languages
        and you want to translate all to unified language. This is handy because it detects
        automatically the language of each sentence and then translate it.

        @param sentences: list of sentences to translate
        @return: list of all translated sentences
        """
        if not sentences:
            raise NotValidPayload(sentences)

        translated_sentences = []
        try:
            for sentence in sentences:
                translated = self.translate(text=sentence, **kwargs)
                translated_sentences.append(translated)

            return translated_sentences

        except Exception as e:
            raise e


if __name__ == '__main__':
    m = MyMemoryTranslator("english", "french").translate("good")
    print(m)

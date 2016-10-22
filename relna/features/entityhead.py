from nalaf.features.relations import EdgeFeatureGenerator
from relna.features.relations import TokenFeatureGenerator
from nltk.stem import PorterStemmer
import re


class EntityHeadTokenFeatureGenerator(EdgeFeatureGenerator):
    """
    Calculate the head token for each entity, using a simple heuristic - the
    distance to the root of the sentence.

    If the entity has just one token, then that forms the head token.
    If the entity has multiple tokens, then the token which is closest to the
    root of the sentence forms the entity head.

    :param feature_set: the feature set for the dataset
    :type feature_set: nalaf.structures.data.FeatureDictionary
    :param training_mode: whether the mode is training or testing, default True
    :type training_mode: bool
    """
    def __init__(self):
        self.stemmer = PorterStemmer()
        """an instance of the PorterStemmer"""


    def generate(self, dataset, feature_set, is_training_mode):
        for edge in dataset.edges():
            entity1 = edge.entity1
            entity2 = edge.entity2

            self.named_entity_count('entity1_', entity1.class_id, edge, feature_set, is_training_mode)
            self.named_entity_count('entity2_', entity2.class_id, edge, feature_set, is_training_mode)

            entity1_stem = self.stemmer.stem(entity1.head_token.word)
            entity1_non_stem = entity1.head_token.word[len(entity1_stem):]
            entity2_stem = self.stemmer.stem(entity2.head_token.word)
            entity2_non_stem = entity1.head_token.word[len(entity2_stem):]

            feature_name_1_1 = '7_entity1_txt_' + entity1.head_token.word + '_[0]'
            feature_name_2_1 = '7_entity2_txt_' + entity2.head_token.word + '_[0]'
            feature_name_1_2 = '8_entity1_pos_' + entity1.head_token.features['pos'] + '_[0]'
            feature_name_2_2 = '8_entity2_pos_' + entity2.head_token.features['pos'] + '_[0]'
            feature_name_1_3 = '9_entity1_stem_' + entity1_stem + '_[0]'
            feature_name_2_3 = '9_entity2_stem_' + entity2_stem + '_[0]'
            feature_name_1_4 = '10_entity1_nonstem_' + entity1_non_stem + '_[0]'
            feature_name_2_4 = '10_entity2_nonstem_' + entity2_non_stem + '_[0]'

            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1_1)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2_1)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1_2)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2_2)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1_3)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2_3)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1_4)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2_4)


    def named_entity_count(self, prefix, entity_type, edge, feature_set, is_training_mode):
        entities = edge.part.get_entities_in_sentence(edge.sentence_id, entity_type)
        feature_name = '1_'+prefix+entity_type+'_count_['+str(len(entities))+']'
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name)


class EntityHeadTokenUpperCaseFeatureGenerator(EdgeFeatureGenerator):
    """
    Check if the head token for the entity has an upper case start

    Value of 1 indicates that the entity starts with an upper case letter
    """
    def __init__(self):
        pass


    def generate(self, dataset, feature_set, is_training_mode):
        feature_name_1 = '11_entity1_upper_case_start_[0]'
        feature_name_2 = '11_entity2_upper_case_start_[0]'
        feature_name_3 = '12_entity1_upper_case_middle_[0]'
        feature_name_4 = '12_entity2_upper_case_middle_[0]'
        for edge in dataset.edges():
            head1 = edge.entity1.head_token
            head2 = edge.entity2.head_token
            if self.training_mode:
                if head1.word[0].isupper():
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
                if head2.word[0].isupper():
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)
                if not head1.word.isupper() and not head1.word.islower():
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_3)
                if not head2.word.isupper() and not head2.word.islower():
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_4)


class EntityHeadTokenDigitsFeatureGenerator(EdgeFeatureGenerator):
    """
    Checks if the head token for the entities in the edge contain a digit.
    If there is a digit, the corresponding feature value is set to 1
    """
    def __init__(self):
        self._digits = re.compile('\d')
        """search regular expression for presence of digits"""


    def generate(self, dataset, feature_set, is_training_mode):
        for edge in dataset.edges():
            head1 = edge.entity1.head_token
            head2 = edge.entity2.head_token
            feature_name_1 = '13_entity1_has_digits_[0]'
            feature_name_2 = '13_entity2_has_digits_[0]'
            feature_name_3 = '14_entity1_has_hyphenated_digits_[0]'
            feature_name_4 = '14_entity2_has_hyphenated_digits_[0]'
            if self.training_mode:
                if self.contains_digits(head1):
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
                    if self.contains_hyphenated_digits(head1):
                        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_3)

                if self.contains_digits(head2):
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)
                    if self.contains_hyphenated_digits(head2):
                        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_4)

    def contains_digits(self, token):
        return bool(self._digits.search(token.word))

    def contains_hyphenated_digits(self, token):
        span = self._digits.search(token.word)
        if span.start()>0 and token.word[span.start()-1]=='-':
            return True
        return False


class EntityHeadTokenLetterPrefixesFeatureGenerator(EdgeFeatureGenerator):
    """
    Combines groups of 2 or 3 letters for each entity
    """
    def __init__(self):
        pass


    def generate(self, dataset, feature_set, is_training_mode):
        for edge in dataset.edges():
            head1 = edge.entity1.head_token
            head2 = edge.entity2.head_token
            for i in range(len(head1.word)):
                if i>0:
                    feature_name_1 = '15_entity1_dt_' + head1.word[i-1:i+1].lower() + '_[0]'
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
                if i>1:
                    feature_name_2 = '16_entity2_tt_' + head1.word[i-2:i+1].lower() + '_[0]'
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)
            for i in range(len(head2.word)):
                if i>0:
                    feature_name_1 = '15_entity2_dt_' + head2.word[i-1:i+1].lower() + '_[0]'
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
                if i>1:
                    feature_name_2 = '16_entity2_tt_' + head2.word[i-2:i+1].lower() + '_[0]'
                    self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)


class EntityHeadTokenPunctuationFeatureGenerator(EdgeFeatureGenerator):
    """
    Check whether the entity head token has punctuations such as forward slash
    ('/') or hyphen ('-')
    """
    def __init__(self):
        pass


    def generate(self, dataset, feature_set, is_training_mode):
        feature_name_1 = '17_entity1_has_hyphen_[0]'
        feature_name_2 = '18_entity1_has_fslash_[0]'
        feature_name_3 = '17_entity2_has_hyphen_[0]'
        feature_name_4 = '18_entity2_has_fslash_[0]'
        for edge in dataset.edges():
            head1 = edge.entity1.head_token
            head2 = edge.entity2.head_token
            if head1.word.find('-')>=0:
                self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
            if head1.word.find('/')>=0:
                self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)
            if head2.word.find('-')>=0:
                self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_3)
            if head2.word.find('/')>=0:
                self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_4)


class EntityHeadTokenChainFeatureGenerator(EdgeFeatureGenerator):
    """
    Generate chains of dependencies from the token of a given depth
    """

    def __init__(self, depth=3):
        self.depth = depth
        """the depth of the chain to generate"""
        self.stemmer = PorterStemmer()
        """an instance of the PorterStemmer"""
        self.token_feature_generator = TokenFeatureGenerator()
        """an instance of TokenFeatureGenerator"""


    def generate(self, dataset, feature_set, is_training_mode):
        for edge in dataset.edges():
            head1 = edge.entity1.head_token
            head2 = edge.entity2.head_token
            self.build_chains(head1, edge.part.sentences[edge.sentence_id], edge, 'entity1_', '', self.depth, feature_set, is_training_mode)
            self.build_chains(head2, edge.part.sentences[edge.sentence_id], edge, 'entity2_', '', self.depth, feature_set, is_training_mode)
            self.build_token_features(edge, feature_set, is_training_mode)
            self.entity_combination(edge, feature_set, is_training_mode)


    def build_token_features(self, edge, feature_set, is_training_mode):
        sentence = edge.part.sentences[edge.sentence_id]
        for token in sentence:
            if token.is_entity_part(edge.part):
                if token.get_entity(edge.part)==edge.entity1:
                    self.token_feature_generator.token_features(token, 'e1_', edge, feature_set, is_training_mode)
                if token.get_entity(edge.part)==edge.entity2:
                    self.token_feature_generator.token_features(token, 'e2_', edge, feature_set, is_training_mode)


    def build_chains(self, token, sentence, edge, prefix, chain, depth_left, feature_set, is_training_mode):
        if depth_left==0:
            return
        depth_string = 'dist_'+str(depth_left)+'_'
        feature_name_1 = '19_'+prefix+'dep_'+depth_string+'from_'+token.features['dep']+'_[0]'
        feature_name_2 = '20_'+prefix+'chain_dep_dist_'+str(depth_left)+'_'+chain+'-fw_'+token.features['dep']+'_[0]'
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)
        self.linear_order_features(prefix+depth_string, token.features['dependency_from'][0], edge, sentence, feature_set, is_training_mode)
        self.build_chains(token.features['dependency_from'][0], sentence, edge, prefix, chain+'-fw', depth_left-1)

        for dependency in token.features['dependency_to']:
            feature_name_1 = '21_'+prefix+'dep_dist_dist_'+str(depth_left)+'_to_'+dependency[1]+'_[0]'
            feature_name_2 = '22_'+prefix+'chain_dep_dist_'+str(depth_left)+'_'+chain+'-rv_'+dependency[1]+'_[0]'
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)
            self.linear_order_features(prefix+'dist_'+str(depth_left)+'_', dependency[0], edge, sentence, feature_set, is_training_mode)
            self.build_chains(dependency[0], sentence, edge, prefix, chain+'-rv', depth_left-1)


    def linear_order_features(self, prefix, token, edge, sentence, feature_set, is_training_mode):
        feature_name_1 = '23_' + prefix + 'txt_' + token.word + '_[0]'
        feature_name_2 = '24_' + prefix + 'pos_' + token.features['pos'] + '_[0]'
        feature_name_3 = '25_' + prefix + 'given_[0]'
        feature_name_4 = '26_' + prefix + 'txt_' + token.masked_text(edge.part) + '_[0]'
        feature_name_5 = '27_' + prefix + 'ann_type_entity_[0]'
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_1)
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_2)
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_3)
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_4)
        if token.is_entity_part(edge.part):
            entity = token.get_entity(edge.part)
            feature_name_6 = '28_' + prefix + 'ann_type_' + entity.class_id + '_[0]'
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_5)
            self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name_6)


    def entity_combination(self, edge, feature_set, is_training_mode):
        feature_name = '29_entity1_'+edge.entity1.class_id+'_entity2_'+edge.entity2.class_id+'_[0]'
        self.add_to_feature_set(feature_set, is_training_mode, edge, feature_name)

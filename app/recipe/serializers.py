from rest_framework import serializers
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class IngredientSerializer(serializers.ModelSerializer):
    """재료 시리얼라이저"""
    class Meta: #  
        model = Ingredient 
        fields = ['id', 'name'] 
        read_only_fields = ['id'] 


class TagSerializer(serializers.ModelSerializer):
    """테그 시리얼라이저"""
    class Meta: #  이 클래스는 시리얼라이저의 메타데이터(설명)를 제공
        model = Tag # Tag 모델에 대한 시리얼라이저
        fields = ['id', 'name'] # 직렬화할 필드들을 지정
        read_only_fields = ['id'] # 읽기 전용

class RecipeSerializer(serializers.ModelSerializer):
    # Tag시리얼라이저랑 잇기 위해 선언
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create( # 이미 있으면 get없으면 crate해주는애.
                user=auth_user,
                **tag, # name=tag['name']할수도있지만 나중에 필드가 추가될수있으니까
            )
            recipe.tags.add(tag_obj)


    def create(self, validated_data):
        tags = validated_data.pop('tags', []) #tag에 있는거를 제거하고 tags에 저장.
        recipe = Recipe.objects.create(**validated_data)
        # 따로따로 다른 modl에 저장해야 하니까 분리함. 
        self._get_or_create_tags(tags, recipe)

        return recipe
    
    def update(self, instance, validated_data):
        # instance는 업데이트할 모델 객체를 나타냄.
        # instance : 예전데이터 validated_data: 바꿀데이터

        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

      
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        




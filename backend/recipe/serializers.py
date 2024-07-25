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
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        # 현재 요청을 보낸 인증된 사용자를 가져옵니다
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create( # 이미 있으면 get없으면 create.
                # tag_obj: 가져오거나 생성된 태그 객체
                # created: 태그가 새로 생성되었는지 여부를 나타내는 불리언 값입니다
                user=auth_user,
                **tag, # name=tag['name']할수도있지만 나중에 필드가 추가될수있으니까
            )
            recipe.tags.add(tag_obj)
            # recipe.tags.add(tag_obj) 부분은 태그 객체(tag_obj)를 레시피 객체(recipe)의 tags 필드에 추가하기 위해 사용됩니다.
            # 이 과정은 다대다 관계(Many-to-Many)를 설정하기 위한 것입니다

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, create = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', []) #tag에 있는거를 제거하고 tags에 저장.
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        # 따로따로 다른 model에 저장해야 하니까 분리함. 
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe
    
    def update(self, instance, validated_data):
        # instance는 업데이트할 모델 객체를 나타냄.
        # instance : 예전데이터 
        # validated_data: 바꿀데이터

        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

      
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    # 이 클래스는 RecipeSerializer를 상속받아 추가 필드를 포함하도록 확장된 직렬화 클래스
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']
        

class RecipeImageSerializer(serializers.ModelSerializer):
    """레시피 생성 시리얼라이저"""
    class Meta:
        model=Recipe
        fields=['id', 'image']
        # 이 시리얼라이저를 통해 Recipe 모델의 id와 image 필드만 직렬화되거나 역직렬화됩니다
        read_only_fields = ['id']
        # 이 필드는 읽기 전용으로 설정됩니다.
        # 즉, 클라이언트가 id 필드를 수정할 수 없으며, 응답에서만 이 필드를 볼 수 있습니다.
        extra_kwargs = {'image': {'required': 'True'}}
        # {'required': 'True'}는 image 필드가 필수임을 나타냅니다. 
        # 따라서 이미지가 업로드되지 않으면 유효성 검사에서 오류가 발생합니다

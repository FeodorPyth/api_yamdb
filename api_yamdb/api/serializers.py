from rest_framework import serializers

from reviews.models import MyUser


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]+\Z',
    )

    class Meta:
        model = MyUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role'
        ]
        read_only_fields = ['username', 'email', 'role']


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role'
        ]


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]+\Z',
    )

    class Meta:
        model = MyUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role'
        ]

    def validate_username(self, value):
        if 'me' == value:
            raise serializers.ValidationError(
                {'username': 'Имя "me" для пользователя запрещено!'}
            )
        return value


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]+\Z',
    )
    confirmation_code = serializers.CharField(max_length=5, required=True)

    class Meta:
        model = MyUser
        fields = ('username', 'confirmation_code')

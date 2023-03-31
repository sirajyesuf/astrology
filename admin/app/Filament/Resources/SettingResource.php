<?php

namespace App\Filament\Resources;

use App\Filament\Resources\SettingResource\Pages;
use App\Filament\Resources\SettingResource\RelationManagers;
use App\Models\Setting;
use Filament\Forms;
use Filament\Resources\Form;
use Filament\Resources\Resource;
use Filament\Resources\Table;
use Filament\Tables;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class SettingResource extends Resource
{
    protected static ?string $model = Setting::class;

    protected static ?string $navigationIcon = 'heroicon-o-collection';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Textarea::make('start_of_session_prompt')
                ->label('Start of A Session Prompt')
                ->rows(5)
                ->cols(5),
                Forms\Components\Textarea::make('end_of_session_prompt')
                ->label('End of A Session Prompt')
                ->rows(5)
                ->cols(5),
                Forms\Components\Textarea::make('end_of_all_sessions_propmt')
                ->label('End of All Sessions propmt')
                ->rows(5)
                ->cols(5),
                Forms\Components\Textarea::make('astrologer_contact_prompt')
                ->label('Astrologer Contact Prompt')
                ->rows(5)
                ->cols(5) 
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                
                Tables\Columns\TextColumn::make("start_of_session_prompt")
                ->limit(70),
                Tables\Columns\TextColumn::make("end_of_session_prompt")
                ->limit(70),
                Tables\Columns\TextColumn::make("end_of_all_sessions_propmt")
                ->limit(70),
                Tables\Columns\TextColumn::make("astrologer_contact_prompt")
                ->limit(70),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\DeleteBulkAction::make(),
            ]);
    }
    
    public static function getRelations(): array
    {
        return [
            //
        ];
    }
    
    public static function getPages(): array
    {
        return [
            'index' => Pages\ListSettings::route('/'),
            'create' => Pages\CreateSetting::route('/create'),
            'edit' => Pages\EditSetting::route('/{record}/edit'),
        ];
    }    
}

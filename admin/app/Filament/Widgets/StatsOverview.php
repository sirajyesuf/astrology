<?php

namespace App\Filament\Widgets;

use App\Models\History;
use App\Models\Plan;
use App\Models\User;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Card;

class StatsOverview extends BaseWidget
{
    protected function getCards(): array
    {
        return [
            Card::make(Plan::count(),'Total Plans'),
            Card::make(User::where("email",null)->count(),'Total Clients'),
            Card::make(History::count(),'Total Prompts')

        ];
    }
}

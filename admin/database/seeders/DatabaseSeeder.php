<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // \App\Models\User::factory(2)->create();

        // \App\Models\User::factory()->create([
        //     'name' => 'Test User',
        //     'email' => 'test@example.com',
        // ]);

        $plans = [
            [
                'name' => 'basic',
                'number_session' => 1,
                'price' => 3,
                'is_free' => false,
                'promo_code' => null,
                'description' => 'here description about the plan'
            ],
            [
                'name' => 'standard',
                'number_session' => 15,
                'price' => 10,
                'is_free' => false,
                'promo_code' => null,
                'description' => 'here description about the plan'

            ],
            [
                'name' => 'free',
                'number_session' => 1,
                'promo_code' => 'freeETH',
                'is_free' => true,
                'price' => null,
                'description' => 'here description about the plan'

            ],


        ];


        DB::table('plans')->truncate();
        DB::table('plans')->insert($plans);

        
    }
}
